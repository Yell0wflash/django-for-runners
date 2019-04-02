# coding: utf-8
from pathlib import Path

import pytest

from django.core.files.uploadedfile import UploadedFile

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.BrowserDebug import debug_response
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel
from for_runners.version import __version__

BASE_PATH = Path(__file__).parent


class ForRunnerAdminTests(TestUserMixin, BaseTestCase):
    """
        Special for runners admin tests
    """

    def test_staff_upload(self):
        self.login(usertype="superuser")

        gpx_file_path1 = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")
        gpx_file_path2 = Path(BASE_PATH, "fixture_files/no_track_points.gpx")

        with gpx_file_path1.open("rb") as file1, gpx_file_path2.open("rb") as file2:

            response = self.client.post(
                "/en/admin/for_runners/gpxmodel/upload/",
                data={
                    "gpx_files": [
                        UploadedFile(file=file1, name=gpx_file_path1.name, content_type="application/gpx+xml"),
                        UploadedFile(file=file2, name=gpx_file_path2.name, content_type="application/gpx+xml"),
                    ]
                },
                HTTP_ACCEPT_LANGUAGE="en",
            )
            # debug_response(response)

        tracks = GpxModel.objects.all()
        self.assertEqual(tracks.count(), 1)
        new_track = tracks[0]

        self.assertRedirects(
            response,
            expected_url="/en/admin/for_runners/gpxmodel/%i/change/" % new_track.pk,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )

        response = self.client.get("/en/admin/for_runners/gpxmodel/", HTTP_ACCEPT_LANGUAGE="en")
        # print(repr(self.get_messages(response)))
        self.assertResponse(
            response,
            must_contain=(
                "<title>Select GPX Track to change | Django-ForRunners v%s</title>" % __version__,
                # "Process garmin_connect_1.gpx...",
                # "Created: 2018-02-21 14:30:50 Moers Hülsdonk",
                #
                # "Process no_track_points.gpx...",
                # "Error process GPX data: Can't get first track",
                '<td class="field-human_pace">7:03 min/km</td>',
                '<p class="paginator">1 GPX Track</p>',
            ),
            messages=[
                "Process garmin_connect_1.gpx...",
                "Created: 2018-02-21 Moers Hülsdonk",
                "Process no_track_points.gpx...",
                "Error process GPX data: Can't get first track",
            ],
            must_not_contain=("error", "traceback"),
            template_name="admin/for_runners/gpxmodel/change_list.html",
            html=True,
        )

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
