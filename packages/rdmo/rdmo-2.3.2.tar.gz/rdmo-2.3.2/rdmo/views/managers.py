from django.db.models import Manager, Q, QuerySet

from rdmo.core.managers import (
    AvailabilityManagerMixin,
    AvailabilityQuerySetMixin,
    CurrentSiteManagerMixin,
    CurrentSiteQuerySetMixin,
    GroupsManagerMixin,
    GroupsQuerySetMixin,
)


class ViewQuerySet(CurrentSiteQuerySetMixin, GroupsQuerySetMixin, AvailabilityQuerySetMixin, QuerySet):

    def filter_catalog(self, catalog):
        return self.filter(Q(catalogs=None) | Q(catalogs=catalog))

    def filter_for_project_site(self, site):
        return self.filter(Q(sites=None) | Q(sites=site))

    def filter_for_project_group(self, groups):
        return self.filter(Q(groups=None) | Q(groups__in=groups))

    def filter_for_project(self, project):
        return (
            self
                .filter(available=True)
                .filter_for_project_site(project.site)
                .filter_catalog(project.catalog)
                .filter_for_project_group(project.groups)
        )

class ViewManager(CurrentSiteManagerMixin, GroupsManagerMixin, AvailabilityManagerMixin, Manager):

    def get_queryset(self) -> ViewQuerySet:
        return ViewQuerySet(self.model, using=self._db)

    def filter_catalog(self, catalog):
        return self.get_queryset().filter_catalog(catalog)

    def filter_for_project(self, project):
        return self.get_queryset().filter_for_project(project)
