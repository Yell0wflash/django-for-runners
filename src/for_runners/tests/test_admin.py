from pathlib import Path

import requests_mock
from django.core.files.uploadedfile import UploadedFile
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin
from override_storage import locmem_stats_override_storage

from for_runners import __version__
from for_runners.models import GpxModel
from for_runners.tests.fixture_files import FIXTURES_PATH, fixture_content
from for_runners.tests.utils import ClearCacheMixin


class ForRunnerAdminTests(TestUserMixin, ClearCacheMixin, BaseTestCase):
    """
        Special for runners admin tests
    """

    def test_staff_upload(self):
        self.login(usertype="superuser")

        gpx_file_path1 = Path(FIXTURES_PATH, "garmin_connect_1.gpx")
        gpx_file_path2 = Path(FIXTURES_PATH, "no_track_points.gpx")

        with gpx_file_path1.open("rb") as file1, gpx_file_path2.open("rb") as file2,\
                locmem_stats_override_storage() as storage_stats,\
                requests_mock.mock() as m:
            m.get(
                'https://www.metaweather.com/api/location/search/?lattlong=51.44,6.62',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_5144_662.json')
            )
            m.get(
                'https://www.metaweather.com/api/location/648820/2018/2/21/',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_location_648820_2018_2_21.json')
            )

            response = self.client.post(
                "/en/admin/for_runners/gpxmodel/upload/",
                data={
                    "gpx_files": [
                        UploadedFile(
                            file=file1, name=gpx_file_path1.name,
                            content_type="application/gpx+xml"
                        ),
                        UploadedFile(
                            file=file2, name=gpx_file_path2.name,
                            content_type="application/gpx+xml"
                        ),
                    ]
                },
                HTTP_ACCEPT_LANGUAGE="en",
            )
            # debug_response(response)
            assert storage_stats.fields_saved == [
                ('for_runners', 'gpxmodel', 'track_svg'),
                ('for_runners', 'gpxmodel', 'gpx_file')
            ]
            assert storage_stats.fields_read == []

            tracks = GpxModel.objects.all()
            self.assertEqual(tracks.count(), 1)
            new_track = tracks[0]

            self.assertRedirects(
                response,
                expected_url=f"/en/admin/for_runners/gpxmodel/{new_track.pk:d}/change/",
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False,
            )

            response = self.client.get("/en/admin/for_runners/gpxmodel/", HTTP_ACCEPT_LANGUAGE="en")
            # print(repr(self.get_messages(response)))
            self.assertResponse(
                response,
                must_contain=(
                    f"<title>Select GPX Track to change | Django-ForRunners v{__version__}</title>",
                    # "Process garmin_connect_1.gpx...",
                    # "Created: 2018-02-21 14:30:50 Moers",
                    #
                    # "Process no_track_points.gpx...",
                    # "Error process GPX data: Can't get first track",
                    '<td class="field-human_pace">7:03 min/km</td>',
                    '<p class="paginator">1 GPX Track</p>',
                ),
                messages=[
                    "Process garmin_connect_1.gpx...",
                    "Created: 2018-02-21",
                    "Process no_track_points.gpx...",
                    "Error process GPX data: Can't get first track",
                ],
                must_not_contain=("error", "traceback"),
                template_name="admin/for_runners/gpxmodel/change_list.html",
                html=True,
            )
            assert storage_stats.fields_read == []

    def test_add_view_redirect_to_upload(self):
        self.login(usertype="superuser")
        response = self.client.get("/en/admin/for_runners/gpxmodel/add/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(
            response,
            expected_url="/en/admin/for_runners/gpxmodel/upload/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
