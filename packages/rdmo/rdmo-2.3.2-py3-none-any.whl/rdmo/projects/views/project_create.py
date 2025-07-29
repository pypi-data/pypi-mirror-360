import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from rdmo.core.views import ObjectPermissionMixin, RedirectViewMixin
from rdmo.questions.models import Catalog
from rdmo.tasks.models import Task
from rdmo.views.models import View

from ..forms import ProjectForm
from ..mixins import ProjectImportMixin
from ..models import Membership, Project

logger = logging.getLogger(__name__)


class ProjectCreateView(ObjectPermissionMixin, LoginRequiredMixin,
                        RedirectViewMixin, CreateView):
    model = Project
    form_class = ProjectForm
    permission_required = 'projects.add_project'

    def get_form_kwargs(self):
        catalogs = Catalog.objects.filter_current_site() \
                                  .filter_group(self.request.user) \
                                  .filter_availability(self.request.user) \
                                  .order_by('-available', 'order')
        projects = Project.objects.filter_user(self.request.user)

        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({
            'catalogs': catalogs,
            'projects': projects
        })
        return form_kwargs

    def form_valid(self, form):
        # add current site
        form.instance.site = get_current_site(self.request)

        # save the project
        response = super().form_valid(form)

        # add current user as owner
        membership = Membership(project=form.instance, user=self.request.user, role='owner')
        membership.save()

        # add all tasks to project
        if not settings.PROJECT_TASKS_SYNC:
            tasks = Task.objects.filter_for_project(form.instance).filter_availability(self.request.user)
            for task in tasks:
                form.instance.tasks.add(task)

        # add all views to project
        if not settings.PROJECT_VIEWS_SYNC:
            views = View.objects.filter_for_project(form.instance).filter_availability(self.request.user)
            for view in views:
                form.instance.views.add(view)

        return response


class ProjectCreateImportView(ObjectPermissionMixin, LoginRequiredMixin,
                              ProjectImportMixin, TemplateView):
    success_url = reverse_lazy('projects')
    permission_required = 'projects.add_project'

    def get(self, request, *args, **kwargs):
        self.object = None

        if kwargs.get('format') is None:
            return self.import_form()
        else:
            return self.get_import_plugin(self.kwargs.get('format'), self.object).render()

    def post(self, request, *args, **kwargs):
        self.object = None

        method = request.POST.get('method')
        if method in ['upload_file', 'import_file']:
            return getattr(self, method)()
        else:
            return self.get_import_plugin(self.kwargs.get('format'), self.object).submit()
