import json
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from bookings.models import Booking, PersonTypeChoices, BookingType
from inventory.models import Club, Unit, Period

@method_decorator(cache_page(120), name='dispatch')
class AnalyticsDashboardView(TemplateView):
    template_name = "admin/analytics_dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()
        classifications = list(filter(None, Unit.objects.values_list('classification', flat=True).distinct()))
        context['classifications'] = classifications
        context['person_types'] = PersonTypeChoices.choices
        context['booking_types'] = BookingType.choices
        context['periods'] = Period.objects.all().order_by('start_date')
        years = Booking.objects.dates('start_date', 'year')
        context['years'] = sorted([d.year for d in years], reverse=True)
        return context

@method_decorator(cache_page(60), name='dispatch')
class AnalyticsDataApiView(APIView):
    def get(self, request, *args, **kwargs):
        qs = Booking.objects.exclude(status='ملغي')
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        year = request.query_params.get('year')
        club_id = request.query_params.get('club_id')
        classification_id = request.query_params.get('classification_id')
        unit_id = request.query_params.get('unit_id')
        person_type = request.query_params.get('person_type')
        booking_type = request.query_params.get('booking_type')
        period_id = request.query_params.get('period_id')
        
        if start_date:
            qs = qs.filter(start_date__gte=start_date)
        if end_date:
            qs = qs.filter(start_date__lte=end_date)
        if year and year != 'all':
            qs = qs.filter(start_date__year=year)
        if club_id and club_id != 'all':
            qs = qs.filter(unit__floor__building__club_id=club_id)
        if classification_id and classification_id != 'all':
            qs = qs.filter(unit__classification=classification_id)
        if unit_id and unit_id != 'all':
            qs = qs.filter(unit_id=unit_id)
        if person_type and person_type != 'all':
            qs = qs.filter(person_type=person_type)
        if booking_type and booking_type != 'all':
            qs = qs.filter(booking_type=booking_type)
        if period_id and period_id != 'all':
            qs = qs.filter(period_id=period_id)

        month = request.query_params.get('month')
        if month and month != 'all':
            qs = qs.filter(start_date__month=month)

        total_bookings = qs.filter(status__in=['مؤكد', 'مكتمل']).count()
        # Revenue should only count confirmed/completed bookings!
        total_revenue = qs.filter(status__in=['مؤكد', 'مكتمل']).aggregate(sum=Sum('total_price'))['sum'] or 0
        total_paid_revenue = qs.filter(status='مؤكد').aggregate(sum=Sum('total_price'))['sum'] or 0

        tree_data = list(qs.values('booking_type', 'status', 'person_type', 'army_region', 'pay_method', 'guest_id_no', 'guest_name', 'unit__allocation')
                           .annotate(count=Count('id'), rev=Sum('total_price')))

        # Helper to initialize nodes
        def node(): return {'c': 0, 'r': 0}

        tree = {
            'global_pt': {'civ': {'c':0,'r':0}, 'mil': {'c':0,'r':0}, 'fam': {'c':0,'r':0}, 'mar': {'c':0,'r':0}, 'vet': {'c':0,'r':0}},
            'total_bookings': total_bookings,
            'total_revenue': float(total_revenue),
            'total_paid_revenue': float(total_paid_revenue),
            'payments': {'visa': node(), 'bank': node(), 'unpaid': node()},
            'standard': {'t': node(), 'civ': node(), 'mil': node(), 'fam': node(), 'mar': node(), 'vet': node()},
            'armies': {'t': node(), 'list': {}},
            'lottery': {
                't': node(),
                'confirmed': {'t': node(), 'mil': node(), 'fam': node()},
                'unconfirmed': {'t': node(), 'mil': node(), 'fam': node()},
            },
            'allocations': {'t': node(), 'admin': node(), 'commander': node(), 'corporate': node(), 'permanent': node()},
            'global_pt': {'civ': node(), 'mil': node(), 'fam': node(), 'mar': node(), 'vet': node()}
        }

        for item in tree_data:
            bt = item['booking_type']
            pt = item['person_type']
            st = item['status']
            ar = item['army_region']
            pm = int(item.get('pay_method') or 0)
            gid = item.get('guest_id_no') or ''
            
            raw_c = item['count']
            raw_r = float(item['rev'] or 0)
            
            # Is it confirmed/completed?
            is_confirmed = st in ['مؤكد', 'مكتمل']
            
            # Only accumulate counts & revenues for the main charts if confirmed
            c = raw_c if is_confirmed else 0
            r = raw_r if is_confirmed else 0.0

            # 1. Global Person Types (Main Charts) - confirmed only
            if pt in ['CIVILIAN_GENERAL', 'CIVILIAN_AF']: 
                tree['global_pt']['civ']['c'] += c
                tree['global_pt']['civ']['r'] += r
            elif pt in ['MILITARY', 'ACTIVE_MEMBER']: 
                tree['global_pt']['mil']['c'] += c
                tree['global_pt']['mil']['r'] += r
            elif pt == 'FAMILY_MEMBER': 
                tree['global_pt']['fam']['c'] += c
                tree['global_pt']['fam']['r'] += r
            elif pt == 'MARTYR': 
                tree['global_pt']['mar']['c'] += c
                tree['global_pt']['mar']['r'] += r
            elif pt == 'VETERAN': 
                tree['global_pt']['vet']['c'] += c
                tree['global_pt']['vet']['r'] += r

            # 2. Payments - we use raw_c and raw_r because "Unpaid" implies unconfirmed, and they need to see how many unpaid there are!
            if pm == 1:
                tree['payments']['visa']['c'] += raw_c
                tree['payments']['visa']['r'] += raw_r
            elif pm == 2:
                tree['payments']['bank']['c'] += raw_c
                tree['payments']['bank']['r'] += raw_r
            else:
                tree['payments']['unpaid']['c'] += raw_c
                tree['payments']['unpaid']['r'] += raw_r

            # 3. Booking Types
            if bt == BookingType.STANDARD:
                tree['standard']['t']['c'] += c
                tree['standard']['t']['r'] += r
                
                if pt in ['CIVILIAN_GENERAL', 'CIVILIAN_AF']: 
                    tree['standard']['civ']['c'] += c
                    tree['standard']['civ']['r'] += r
                elif pt in ['MILITARY', 'ACTIVE_MEMBER']: 
                    tree['standard']['mil']['c'] += c
                    tree['standard']['mil']['r'] += r
                elif pt == 'FAMILY_MEMBER': 
                    tree['standard']['fam']['c'] += c
                    tree['standard']['fam']['r'] += r
                elif pt == 'MARTYR': 
                    tree['standard']['mar']['c'] += c
                    tree['standard']['mar']['r'] += r
                elif pt == 'VETERAN': 
                    tree['standard']['vet']['c'] += c
                    tree['standard']['vet']['r'] += r

            elif bt == BookingType.ARMIES_REGIONS:
                tree['armies']['t']['c'] += c
                tree['armies']['t']['r'] += r
                if ar:
                    if ar not in tree['armies']['list']:
                        tree['armies']['list'][ar] = node()
                    tree['armies']['list'][ar]['c'] += c
                    tree['armies']['list'][ar]['r'] += r

            elif bt == BookingType.LOTTERY:
                tree['lottery']['t']['c'] += c
                tree['lottery']['t']['r'] += r
                
                # Lottery sub breakdown needs raw values to show Unconfirmed
                sub = 'confirmed' if is_confirmed else 'unconfirmed'
                tree['lottery'][sub]['t']['c'] += raw_c
                tree['lottery'][sub]['t']['r'] += raw_r
                
                if pt == 'MILITARY': 
                    tree['lottery'][sub]['mil']['c'] += raw_c
                    tree['lottery'][sub]['mil']['r'] += raw_r
                elif pt == 'FAMILY_MEMBER': 
                    tree['lottery'][sub]['fam']['c'] += raw_c
                    tree['lottery'][sub]['fam']['r'] += raw_r
                
            elif bt == BookingType.ALLOCATIONS:
                alloc_type = item.get('unit__allocation') or ''
                is_occupied = bool(gid) and gid != ''
                if not is_occupied:
                    tree['allocations']['t']['c'] += c
                    tree['allocations']['t']['r'] += r
                    
                    if alloc_type == 'ADMINISTRATIVE':
                        tree['allocations']['admin']['c'] += c
                        tree['allocations']['admin']['r'] += r
                    elif alloc_type == 'COMMANDER':
                        tree['allocations']['commander']['c'] += c
                        tree['allocations']['commander']['r'] += r
                    elif alloc_type == 'COMPANY':
                        tree['allocations']['corporate']['c'] += c
                        tree['allocations']['corporate']['r'] += r
                    elif alloc_type == 'PERMANENT':
                        tree['allocations']['permanent']['c'] += c
                        tree['allocations']['permanent']['r'] += r

        # Chart Data (Only count confirmed/completed for revenue charts)
        qs_confirmed = qs.filter(status__in=['مؤكد', 'مكتمل'])
        club_rev = list(qs_confirmed.values('unit__floor__building__club__name')
                          .annotate(rev=Sum('total_price'), count=Count('id'))
                          .order_by('-rev'))
        
        trend = list(qs_confirmed.annotate(month=TruncMonth('start_date'))
                       .values('month')
                       .annotate(rev=Sum('total_price'), count=Count('id'))
                       .order_by('month'))

        return Response({
            'tree': tree,
            'charts': {
                'club_distribution': club_rev,
                'trend': trend
            }
        })
