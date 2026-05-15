from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from experiments.models import Assignment, Device, Experiment, Variant


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    inlines = [VariantInline]
    list_display = ("key", "name", "is_active", "created_at")

    def get_urls(self):
        return [
            path("stats/", self.admin_site.admin_view(self.stats_view), name="stats"),
            *super().get_urls(),
        ]

    def stats_view(self, request):
        experiments = Experiment.objects.filter(is_active=True).prefetch_related(
            "variants", "variants__assignments"
        )
        rows = []
        for exp in experiments:
            total_devices = (
                Assignment.objects.filter(experiment=exp)
                .values("device")
                .distinct()
                .count()
            )
            variant_stats = []
            for v in exp.variants.all():
                count = v.assignments.count()
                pct = (count / total_devices * 100) if total_devices else 0
                variant_stats.append(
                    {"value": v.value, "weight": v.weight, "count": count, "pct": round(pct, 1)}
                )
            rows.append(
                {
                    "key": exp.key,
                    "name": exp.name,
                    "total_devices": total_devices,
                    "variants": variant_stats,
                }
            )
        return TemplateResponse(
            request,
            "admin/stats.html",
            {"rows": rows},
        )


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("token", "created_at")
    search_fields = ("token",)
