"""Admin site."""

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveGroup, EveType

from fleetcomp.models import FleetMember, FleetSnapshot, ShipGrouping

# Register your models for the admin site here.

EVE_SHIP_CATEGORY_ID = 6


class FleetMembersInline(admin.TabularInline):
    model = FleetMember

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@admin.register(FleetSnapshot)
class FleetSnapshotAdmin(admin.ModelAdmin):
    list_display = ["commander", "timestamp", "fleet_id"]
    inlines = [FleetMembersInline]

    def has_change_permission(self, request, obj=...):
        return False


class CustomGroupingFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["associated_types"].queryset = EveType.objects.filter(
            eve_group__eve_category=EVE_SHIP_CATEGORY_ID
        ).order_by("name")
        self.fields["associated_groups"].queryset = EveGroup.objects.filter(
            eve_category=EVE_SHIP_CATEGORY_ID
        ).order_by("name")


@admin.register(ShipGrouping)
class ShipGroupingAdmin(admin.ModelAdmin):
    list_display = ["display_name", "column_index", "ship_types", "ship_groups"]
    form = CustomGroupingFrom
    ordering = ["column_index"]

    @admin.display(description=_("Ship types"))
    def ship_types(self, custom_grouping: ShipGrouping):
        return ", ".join(
            custom_grouping.associated_types.values_list("name", flat=True)
        )

    @admin.display(description=_("Ship groups"))
    def ship_groups(self, custom_grouping: ShipGrouping):
        return ", ".join(
            custom_grouping.associated_groups.values_list("name", flat=True)
        )
