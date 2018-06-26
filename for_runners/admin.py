"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import io
import logging
import math
import statistics
from datetime import date
from pprint import pprint

from autotask.tasks import delayed_task
from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db import IntegrityError, models
from django.db.models import Avg, Max, Min
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views import View, generic
# https://github.com/jedie/django-for-runners
from django.views.generic.base import TemplateResponseMixin, TemplateView
from for_runners import constants
from for_runners.exceptions import GpxDataError
from for_runners.forms import (INITIAL_DISTANCE, DistanceStatisticsForm, UploadGpxFileForm)
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy
from for_runners.gpx_tools.gpxpy2map import generate_map
from for_runners.models import (DisciplineModel, EventLinkModel, EventModel, GpxModel)

log = logging.getLogger(__name__)



STATISTICS_CHOICES=(
    (constants.DISPLAY_DISTANCE_PACE_KEY, _('Distance/Pace')),
    (constants.DISPLAY_PACE_DURATION, _('Pace/Duration')),
    (constants.DISPLAY_GPX_INFO, _('GPX info')),
    (constants.DISPLAY_GPX_METADATA, _('GPX metadata')),
)
assert len(dict(STATISTICS_CHOICES)) == len(STATISTICS_CHOICES), "Double keys?!?"


@admin.register(DisciplineModel)
class DisciplineModelAdmin(admin.ModelAdmin):
    pass


@admin.register(EventLinkModel)
class EventLinkModelAdmin(admin.ModelAdmin):
    pass


class LinkModelInline(admin.TabularInline):
    model = EventLinkModel
    extra = 2
    min_num = 1
    max_num = None
    fields = (
        'url',
        'text',
        'title',
    )


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):
    list_display = ("verbose_name", "links_html", "start_time", "discipline")
    list_display_links = ("verbose_name",)
    inlines = [
        LinkModelInline,
    ]


class UploadGpxFileView(generic.FormView):
    template_name = "for_runners/upload_gpx_file.html"
    form_class = UploadGpxFileForm
    success_url = "../"  # FIXME

    def post(self, request, *args, **kwargs):
        user = request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist("gpx_files")
        if form.is_valid():
            log.debug("files: %r", files)
            for f in files:
                messages.info(request, "Process %s..." % f.name)

                content = f.file.read()
                log.debug("raw content......: %s", repr(content)[:100])
                content = content.decode("utf-8")
                log.debug("decoded content..: %s", repr(content)[:100])

                try:
                    try:
                        gpx = GpxModel.objects.create(gpx=content, tracked_by=user)
                    except IntegrityError as err:
                        messages.error(request, "Error process GPX data: %s" % err)
                        continue

                    gpx.calculate_values()
                except GpxDataError as err:
                    messages.error(request, "Error process GPX data: %s" % err)
                else:
                    messages.success(request, "Created: %s" % gpx)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ChangelistViewMixin:

    def dispatch(self, request, change_list, *args, **kwargs):
        self.change_list = change_list
        return super().dispatch(request, *args, **kwargs)


class BaseChangelistView(ChangelistViewMixin, TemplateView):
    """
    Baseclass for chnagelist views without forms.
    """
    pass


class BaseFormChangelistView(ChangelistViewMixin, generic.FormView):
    """
    Baseclass for chnagelist views with forms.
    """
    form_class = None

    def form_valid(self, form):
        # Don't redirect, if form is valid ;)
        return self.render_to_response(self.get_context_data(form=form))


class DistancePaceStatisticsView(BaseChangelistView):
    template_name = "for_runners/distance_pace_statistics.html"

    def get_context_data(self, **kwargs):
        qs = self.change_list.queryset  # get the filteres queryset form GpxModelChangeList
        qs = qs.order_by("length")
        context = {
            "tracks":qs,
            "track_count": qs.count(),
            "title": _("Distance/Pace Statistics"),
            "user": self.request.user,
            "opts": GpxModel._meta,
        }
        return context


class DistanceStatisticsView(BaseFormChangelistView):
    template_name = "for_runners/distance_statistics.html"
    form_class = DistanceStatisticsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context["form"]
        if form.is_valid():
            distance = form.cleaned_data["distance"]
        else:
            distance = INITIAL_DISTANCE

        distance_m = distance * 1000

        qs = self.change_list.queryset  # get the filteres queryset form GpxModelChangeList
        qs = qs.order_by("length")

        length_statistics = qs.aggregate(Min('length'), Avg("length"), Max('length'))

        min_length = length_statistics["length__min"]
        max_length = length_statistics["length__max"]

        current_distance_from = math.floor(min_length / 1000) * 1000
        current_distance_to = current_distance_from + distance_m

        group_data = collections.defaultdict(list)
        for track in qs:
            length = track.length
            # print("%.1fkm" % round(length/1000,1))
            if length > current_distance_to:
                while True:
                    current_distance_from += distance_m
                    current_distance_to += distance_m
                    if length > current_distance_to:
                        group_data[(current_distance_from, current_distance_to)] = []
                    else:
                        break

            group_data[(current_distance_from, current_distance_to)].append(track)

        print("group_data:")
        pprint(group_data)

        track_data = []
        total_tracks = 0
        for distances, tracks in sorted(group_data.items()):
            track_count = len(tracks)
            total_tracks += track_count
            distance_from, distance_to = distances

            if tracks:
                paces = [track.pace for track in tracks]
                min_paces = "%.2f" % min(paces)
                avg_paces = "%.2f" % statistics.median(paces)
                max_paces = "%.2f" % max(paces)
            else:
                min_paces = "null"
                avg_paces = "null"
                max_paces = "null"

            track_data.append((
                round(distance_from / 1000, 1), round(distance_to / 1000, 1), track_count, min_paces, avg_paces,
                max_paces
            ))
        print("total track counts:", total_tracks)
        pprint(track_data)

        context.update({
            "tracks": qs,
            "track_count": total_tracks,
            "min_length_km": round(min_length / 1000),
            "avg_length_km": round(length_statistics["length__avg"] / 1000),
            "max_length_km": round(max_length / 1000),
            "track_data": track_data,

            "title": _("Distance Statistics"),
            "user": self.request.user,
            "opts": GpxModel._meta,

        })
        # pprint(context)
        return context


class GpxInfoView(BaseChangelistView):
    template_name = "for_runners/gpx_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.change_list.queryset  # get the filteres queryset form GpxModelChangeList

        context.update({
            "tracks": qs,

            "title": _("GPX Infomation"),
            "user": self.request.user,
            "opts": GpxModel._meta,
        })
        return context


class GpxMetadataView(BaseChangelistView):
    template_name = "for_runners/gpx_metadata.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "tracks": self.change_list.queryset,  # get the filteres queryset form GpxModelChangeList,

            "title": _("GPX Metadata"),
            "user": self.request.user,
            "opts": GpxModel._meta,
        })
        return context


class ProcessGpxDataView(generic.View):

    def get(self, request, object_id):
        """
        Create delayed task to generate the map of the GPX Track
        """
        messages.info(request, "GPX Map will be generated in background")

        gpx_instance = GpxModel.objects.get(pk=object_id)
        gpx_instance.schedule_generate_map()

        return HttpResponseRedirect("../")


class CalculateValuesView(generic.View):

    def get(self, request, object_id):
        instance = GpxModel.objects.get(pk=object_id)
        instance.calculate_values()
        instance.save()
        messages.success(request, "Values are calculated from GPX data")
        return HttpResponseRedirect("../")


class StatisticsListFilter(admin.SimpleListFilter):
    title = _('statistics')
    template = 'admin/filter.html'  # TODO: Use own template and change output

    # Parameter for the filter that will be used in the URL query.
    parameter_name = constants.STATISTICS_PARAMETER_NAME

    def lookups(self, request, model_admin):
        return STATISTICS_CHOICES

    def queryset(self, request, queryset):
        return queryset


class GpxModelChangeList(ChangeList):

    def __init__(self, *args, **kwargs):
        self.startistics_mapping = {
            constants.DISPLAY_DISTANCE_PACE_KEY: DistanceStatisticsView,
            constants.DISPLAY_PACE_DURATION: DistancePaceStatisticsView,
            constants.DISPLAY_GPX_INFO: GpxInfoView,
            constants.DISPLAY_GPX_METADATA: GpxMetadataView,
        }
        super().__init__(*args, **kwargs)

    def get_results(self, request):
        super(GpxModelChangeList, self).get_results(request)

        self.statistics = ""

        if constants.STATISTICS_PARAMETER_NAME in request.GET:
            if self.result_count == 0:
                log.debug("No tracks: no statistics.")
                return

            key = request.GET[constants.STATISTICS_PARAMETER_NAME]
            try:
                ViewClass = self.startistics_mapping[key]
            except KeyError as err:
                log.error("statistic view unknown: %s", err)
            else:
                view = ViewClass.as_view()
                response = view(request, self)
                assert isinstance(response, TemplateResponse), "Method %s didn't return a TemplateResponse!" % view
                self.statistics = response.rendered_content


@admin.register(GpxModel)
class GpxModelAdmin(admin.ModelAdmin):
    search_fields = (
        "full_start_address",
        "full_finish_address",
    )
    list_display = (
        "svg_tag", "overview", "start_time", "human_length", "human_duration", "human_pace", "heart_rate_avg",
        "human_weather", "uphill", "downhill", "min_elevation", "max_elevation", "tracked_by"
    )
    list_filter = (
        StatisticsListFilter,
        "tracked_by",
        "start_time",
    )
    list_per_page = 50
    list_display_links = (
        "svg_tag",
        "overview",
    )
    readonly_fields = (
        "leaflet_map_html", "chartjs_html", "svg_tag_big", "image_tag", "svg_tag", "start_time", "start_latitude",
        "start_longitude", "finish_time", "finish_latitude", "finish_longitude", "start_coordinate_html",
        "finish_coordinate_html", "heart_rate_min", "heart_rate_avg", "heart_rate_max"
    )

    fieldsets = (
        (_("Event"), {
            "fields": (
                "event",
                "leaflet_map_html",
                "chartjs_html",
                ("map_image", "image_tag"),
            )
        }),
        (_("Start"), {
            "fields": (
                ("start_time", "start_temperature", "start_weather_state"),
                "short_start_address",
                "full_start_address",
                "start_coordinate_html",
                ("start_latitude", "start_longitude"),
            )
        }),
        (_("Finish"), {
            "fields": (
                ("finish_time", "finish_temperature", "finish_weather_state"),
                "short_finish_address",
                "full_finish_address",
                "finish_coordinate_html",
                ("finish_latitude", "finish_longitude"),
            )
        }),
        (_("GPX data"), {
            "classes": ("collapse",),
            "fields": (
                ("gpx", "points_no"),
                ("track_svg", "svg_tag_big"),
            )
        }),
        (_("Values"), {
            "fields": (
                ("length", "duration", "pace"),
                ("heart_rate_min","heart_rate_avg","heart_rate_max"),
                ("uphill", "downhill"),
                ("min_elevation", "max_elevation"),
            )
        }),
    )
    # FIXME: Made this in CSS ;)
    formfield_overrides = {models.CharField: {'widget': forms.TextInput(attrs={'style': 'width:70%'})}}

    def overview(self, obj):
        parts = []
        if obj.event:
            parts.append("<strong>%s</strong>" % obj.event)
        parts.append(obj.start_end_address())
        html = "<br>".join(parts)
        return html

    overview.short_description = _("Event")
    overview.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r"^upload/$", self.admin_site.admin_view(UploadGpxFileView.as_view()), name="upload-gpx-file"),
            url(
                r"^distance-statistics/$",
                self.admin_site.admin_view(DistanceStatisticsView.as_view()),
                name="distance-statistics"
            ),
            url(
                r"^distance-pace-statistics/$",
                self.admin_site.admin_view(DistancePaceStatisticsView.as_view()),
                name="distance-pace-statistics"
            ),
            url(
                r"^(.+)/process/$",
                self.admin_site.admin_view(ProcessGpxDataView.as_view()),
                name="%s_%s_process-gpx-data" % info
            ),
            url(
                r"^(.+)/calculate_values/$",
                self.admin_site.admin_view(CalculateValuesView.as_view()),
                name="%s_%s_calculate-values" % info
            ),
        ] + urls
        return urls

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return GpxModelChangeList

    # def changelist_view(self, request, extra_context=None):
    #     if extra_context is None:
    #         extra_context = {}
    #

    #
    #     return super(GpxModelAdmin, self).changelist_view(request, extra_context)
