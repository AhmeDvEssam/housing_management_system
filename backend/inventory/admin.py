from django.contrib import admin
from .models import Club, Building, Floor, Unit


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "created_at")
    search_fields = ("name", "city")
    list_filter = ("city",)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "building_type", "created_at")
    search_fields = ("name", "club__name")
    list_filter = ("building_type", "club")


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("label", "level_number", "building", "created_at")
    search_fields = ("label", "building__name", "building__club__name")
    list_filter = ("building",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "unit_no",
        "unit_type",
        "capacity",
        "floor",
        "get_building",
        "get_club",
        "orientation",
        "is_bookable",
        "is_maintenance",
    )
    search_fields = (
        "unit_no",
        "floor__building__name",
        "floor__building__club__name",
    )
    list_filter = (
        "unit_type",
        "orientation",
        "is_bookable",
        "is_maintenance",
        "floor__building__club",
    )

    @admin.display(description="المبنى")
    def get_building(self, obj: Unit) -> str:
        return obj.floor.building.name

    @admin.display(description="النادي")
    def get_club(self, obj: Unit) -> str:
        return obj.floor.building.club.name
