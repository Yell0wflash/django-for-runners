"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
from urllib.parse import urlparse

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_tools.models import UpdateInfoBaseModel, UpdateTimeBaseModel
from for_runners.models import DisciplineModel

log = logging.getLogger(__name__)


def human_url(url):
    scheme, netloc, url, params, query, fragment = urlparse(url)
    text = netloc + url
    text = text.strip("/")
    if text.startswith("www."):
        text = text[4:]
    return text


class LinkModelBase(UpdateTimeBaseModel):
    url = models.URLField(help_text=_("Link URL"))
    text = models.CharField(
        max_length=127,
        help_text=_("Link text (leave empty to generate it from url)"),
        null=True,
        blank=True,
    )
    title = models.CharField(
        max_length=127,
        help_text=_("Link title (leave empty to generate it from url)"),
        null=True,
        blank=True,
    )

    def get_text(self):
        return self.text or human_url(self.url)

    def get_title(self):
        return self.title or self.url

    def link_html(self):
        return ('<a href="{url}" title="{title}" target="_blank">'
                '{text}'
                '</a>').format(
                    url=self.url, title=self.get_title(), text=self.get_text())

    link_html.short_description = _("Link")
    link_html.allow_tags = True

    def save(self, *args, **kwargs):
        if self.text is None:
            self.text = human_url(self.url)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_text()

    class Meta:
        abstract = True


class EventModel(UpdateInfoBaseModel):
    """
    inherit from UpdateInfoBaseModel:
        * createtime
        * lastupdatetime
        * createby
        * lastupdateby
    """
    no = models.PositiveIntegerField(
        help_text=_("Sequential number of the event"),
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, help_text=_("Name of the event"))
    start_time = models.DateTimeField(
        help_text=_("Start date/time of the run"),
        null=True,
        blank=True,
    )
    discipline = models.ForeignKey(DisciplineModel)

    def verbose_name(self):
        parts = []
        if self.no:
            parts.append("%i." % self.no)
        parts.append(self.name)
        year = self.start_time.strftime("%Y")
        if year not in self.name:
            parts.append(year)
        result = " ".join([part for part in parts if part])
        return result

    verbose_name.short_description = _("Verbose Name")

    def links_html(self):
        links = []
        for link in self.links.all():
            links.append(link.link_html())
        return "<br />".join(links)

    links_html.short_description = _("Links")
    links_html.allow_tags = True

    def __str__(self):
        return "%i. %s %s" % (self.no, self.name,
                              self.start_time.strftime("%Y"))

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ('-start_time', '-pk')


class EventLinkModel(LinkModelBase):
    event = models.ForeignKey(EventModel, related_name="links")
