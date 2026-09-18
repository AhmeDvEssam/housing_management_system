import re
from django import forms
from inventory.models import Club, Unit, Building, Period
from .models import Booking


# Custom widget to force type="date" in the browser (native calendar picker)
class HTML5DateInput(forms.DateInput):
    input_type = 'date'


from django.utils.safestring import mark_safe
from members.models import Member

class BookingAdminForm(forms.ModelForm):
    club = forms.ModelChoiceField(
        queryset=Club.objects.all(),
        label="النادي",
        required=False,
    )
    building = forms.ChoiceField(
        choices=[('', '---------')],
        label="المبنى / الفندق",
        required=False,
    )
    classification = forms.CharField(
        label="التصنيف",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color:#e9ecef;'}),
    )
    unit_type = forms.CharField(
        label="نوع الوحدة",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color:#e9ecef;'}),
    )
    units = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.none(),
        label="الوحدات (للحجز الجماعي)",
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'style': 'display:none;',
        }),
    )

    class Meta:
        model = Booking
        fields = "__all__"
        widgets = {
            'person_type': forms.RadioSelect(attrs={'class': 'inline-radios'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'total_price': forms.NumberInput(attrs={'readonly': 'readonly', 'style': 'background-color:#e9ecef; font-weight: bold; color: green;'}),
            'start_date': HTML5DateInput(attrs={'class': 'form-control'}, format='%Y-%m-%d'),
            'end_date': HTML5DateInput(attrs={'class': 'form-control'}, format='%Y-%m-%d'),
            'payment_deadline': HTML5DateInput(attrs={'class': 'form-control'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sort periods naturally by number (الأسبوع 1, 2, 3, ... 10, 11, ...)
        def period_sort_key(period):
            nums = re.findall(r'\d+', period.name)
            return int(nums[0]) if nums else 0

        sorted_periods = sorted(Period.objects.all(), key=period_sort_key)
        sorted_ids = [p.id for p in sorted_periods]
        # Preserve the sorted order using Case/When
        from django.db.models import Case, When
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])
        self.fields['period'].queryset = Period.objects.filter(pk__in=sorted_ids).order_by(preserved_order)

        # Unit starts empty — JS populates via AJAX
        self.fields['unit'].queryset = Unit.objects.none()
        self.fields['unit'].widget.can_add_related = False
        self.fields['unit'].widget.can_change_related = False
        self.fields['unit'].widget.can_view_related = False

        # Initialize units field safely
        if 'units' in self.fields:
            self.fields['units'].queryset = Unit.objects.none()

        is_editing = self.instance and self.instance.pk and self.instance.unit

        if is_editing:
            # --- EDITING MODE ---
            unit = self.instance.unit
            building = unit.floor.building
            club = building.club

            self.fields['club'].initial = club

            # Build building choices for this club
            buildings = Building.objects.filter(club=club).order_by('name')
            self.fields['building'].choices = [('', '---------')] + [
                (b.id, b.name) for b in buildings
            ]
            self.fields['building'].initial = building.id

            # Unit queryset for this building
            self.fields['unit'].queryset = Unit.objects.filter(floor__building=building)
            self.fields['classification'].initial = unit.classification
            self.fields['unit_type'].initial = unit.get_unit_type_display()

        else:
            # --- ADDING MODE ---
            # unit is optional (user might use bulk mode instead)
            self.fields['unit'].required = False

            if self.data.get('club'):
                # Form was submitted — restore cascading state for validation
                try:
                    club_id = int(self.data.get('club'))
                    buildings = Building.objects.filter(club_id=club_id).order_by('name')
                    self.fields['building'].choices = [('', '---------')] + [
                        (b.id, b.name) for b in buildings
                    ]
                except (ValueError, TypeError):
                    pass

                building_id = self.data.get('building')
                if building_id:
                    try:
                        building_id = int(building_id)
                        self.fields['unit'].queryset = Unit.objects.filter(floor__building_id=building_id)
                    except (ValueError, TypeError):
                        pass

        # Always ensure submitted unit passes validation
        unit_id = self.data.get('unit')
        if unit_id:
            try:
                unit_id = int(unit_id)
                self.fields['unit'].queryset = self.fields['unit'].queryset | Unit.objects.filter(id=unit_id)
            except (ValueError, TypeError):
                pass

        # Always ensure submitted units pass validation (bulk mode)
        if 'units' in self.fields:
            units_ids = self.data.getlist('units')
            if units_ids:
                try:
                    int_ids = [int(i) for i in units_ids if i]
                    self.fields['units'].queryset = Unit.objects.filter(id__in=int_ids)
                except (ValueError, TypeError):
                    pass

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get('unit')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        units = cleaned_data.get('units')

        if start_date and end_date:
            from .models import BookingDay
            from datetime import timedelta

            if end_date <= start_date:
                raise forms.ValidationError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")

            days = []
            curr = start_date
            while curr < end_date:
                days.append(curr)
                curr += timedelta(days=1)

            if not self.instance.pk:
                # Adding new booking
                if units:
                    # Bulk mode
                    cleaned_data['unit'] = list(units)[0]
                    for u in units:
                        conflicts = BookingDay.objects.filter(unit=u, day__in=days)
                        if conflicts.exists():
                            self.add_error('units', f"الوحدة {u} محجوزة بالفعل في هذه الفترة.")
                elif unit:
                    # Single mode
                    conflicts = BookingDay.objects.filter(unit=unit, day__in=days)
                    if conflicts.exists():
                        raise forms.ValidationError("الغرفة دي محجوزة بالفعل في هذه الفترة.")
                else:
                    raise forms.ValidationError("يرجى اختيار وحدة واحدة على الأقل")
            else:
                # Editing existing booking
                if unit:
                    conflicts = BookingDay.objects.filter(unit=unit, day__in=days).exclude(booking=self.instance)
                    if conflicts.exists():
                        self.add_error('unit', "هذه الوحدة محجوزة بالفعل في هذه الفترة.")

        return cleaned_data
