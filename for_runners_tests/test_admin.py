# coding: utf-8

import unittest

import pytest

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.selenium_utils import (
    SeleniumChromiumTestCase,
    SeleniumFirefoxTestCase,
    chromium_available,
    firefox_available,
)
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

# https://github.com/jedie/django-for-runners
from for_runners.version import __version__


@pytest.mark.django_db
class AdminAnonymousTests(BaseTestCase):
    """
    Anonymous will be redirected to the login page.
    """

    def test_login_en(self):
        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(response, expected_url="/en/admin/login/?next=/en/admin/")

    def test_login_de(self):
        response = self.client.get("/de/admin/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertRedirects(response, expected_url="/de/admin/login/?next=/de/admin/")


@pytest.mark.django_db
class AdminLoggedinTests(TestUserMixin, AdminAnonymousTests):
    """
    Some basics test with the django admin
    """

    def test_staff_admin_index(self):
        self.login(usertype="staff")
        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(
            response,
            must_contain=(
                "<title>Site administration | Django-ForRunners v%s</title>" % __version__,
                "<h1>Site administration</h1>",
                "<strong>staff_test_user</strong>",
                "<p>You don't have permission to view or edit anything.</p>",
            ),
            must_not_contain=("error", "traceback", "/add/", "/change/"),
            template_name="admin/index.html",
            messages=[],
            html=True,
        )

    def test_superuser_admin_index(self):
        self.login(usertype="superuser")
        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(
            response,
            must_contain=(
                "Django-ForRunners",
                "superuser",
                "Site administration",
                "/admin/auth/group/add/",
                "/admin/auth/user/add/",
            ),
            must_not_contain=("error", "traceback"),
            template_name="admin/index.html",
        )


@unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
class AdminChromiumTests(SeleniumChromiumTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django-ForRunners v%s" % __version__)
        self.assert_in_page_source('<form action="/en/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()


@unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
class AdminFirefoxTests(SeleniumFirefoxTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django-ForRunners v%s" % __version__)
        self.assert_in_page_source('<form action="/en/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()
