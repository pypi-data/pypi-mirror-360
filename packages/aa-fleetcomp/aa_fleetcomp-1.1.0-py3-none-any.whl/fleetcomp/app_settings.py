"""App settings."""

from django.conf import settings

FLEETCOMP_FLEET_CACHE_MINUTES = getattr(settings, "FLEETCOMP_FLEET_CACHE_MINUTES", 5)
