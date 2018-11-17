"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

from django.core.management.base import BaseCommand

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel
from for_runners.services.gpx import generate_svg

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Recreate all svg files for existing gpx tracks"

    def handle(self, *args, **options):
        qs = GpxModel.objects.all()
        total_count = qs.count()
        for no, gpx_track in enumerate(qs):
            print("[%i/%i] Generate SVG for: %s" % (no, total_count, gpx_track))

            if not gpx_track.gpx:
                continue

            generate_svg(gpx_track=gpx_track, force=True)

            gpx_track.save()
