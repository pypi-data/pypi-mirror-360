from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist

import rules
from rules.predicates import is_superuser


@rules.predicate
def can_add_project(user):
    if not settings.PROJECT_CREATE_RESTRICTED:
        return True

    if settings.PROJECT_CREATE_GROUPS:
        return user.groups.filter(name__in=settings.PROJECT_CREATE_GROUPS).exists()
    else:
        return False


@rules.predicate
def is_project_member(user, project):
    return user in project.member or (project.parent and is_project_member(user, project.parent))


@rules.predicate
def is_current_project_member(user, project):
    return user in project.member


@rules.predicate
def is_project_owner(user, project):
    return user in project.owners or (project.parent and is_project_owner(user, project.parent))


@rules.predicate
def is_project_manager(user, project):
    return user in project.managers or (project.parent and is_project_manager(user, project.parent))


@rules.predicate
def is_project_author(user, project):
    return user in project.authors or (project.parent and is_project_author(user, project.parent))


@rules.predicate
def is_project_guest(user, project):
    return user in project.guests or (project.parent and is_project_guest(user, project.parent))


@rules.predicate
def is_visible(user, project):
    if user.is_authenticated:
        try:
            return project.visibility.is_visible(user)
        except ObjectDoesNotExist:
            return False
    else:
        return False


@rules.predicate
def is_site_manager(user, project):
    if user.is_authenticated:
        return user.role.manager.filter(pk=project.site.pk).exists()
    else:
        return False


@rules.predicate
def is_site_manager_for_current_site(user, request):
    if user.is_authenticated:
        current_site = get_current_site(request)
        return user.role.manager.filter(pk=current_site.pk).exists()
    else:
        return False


# Add rule for check in template
rules.add_rule('projects.can_view_all_projects', is_site_manager_for_current_site | is_superuser)

rules.add_perm('projects.add_project', can_add_project)
rules.add_perm('projects.view_project_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.change_project_object', is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.change_project_progress_object', is_project_author | is_project_manager | is_project_owner | is_site_manager)  # noqa: E501
rules.add_perm('projects.delete_project_object', is_project_owner | is_site_manager)
rules.add_perm('projects.leave_project_object', is_current_project_member)
rules.add_perm('projects.export_project_object', is_project_owner | is_project_manager | is_site_manager)
rules.add_perm('projects.import_project_object', is_project_owner | is_project_manager | is_site_manager)

rules.add_perm('projects.view_visibility_object', is_site_manager)
rules.add_perm('projects.add_visibility_object', is_site_manager)
rules.add_perm('projects.change_visibility_object', is_site_manager)
rules.add_perm('projects.delete_visibility_object', is_site_manager)

rules.add_perm('projects.view_membership_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.add_membership_object', is_project_owner | is_site_manager)
rules.add_perm('projects.change_membership_object', is_project_owner | is_site_manager)
rules.add_perm('projects.delete_membership_object', is_project_owner | is_site_manager)

rules.add_perm('projects.view_invite_object', is_project_owner | is_site_manager)
rules.add_perm('projects.add_invite_object', is_project_owner | is_site_manager)
rules.add_perm('projects.change_invite_object', is_project_owner | is_site_manager)
rules.add_perm('projects.delete_invite_object', is_project_owner | is_site_manager)

rules.add_perm('projects.view_integration_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.add_integration_object', is_project_owner | is_project_manager | is_site_manager)
rules.add_perm('projects.change_integration_object', is_project_owner | is_project_manager | is_site_manager)
rules.add_perm('projects.delete_integration_object', is_project_owner | is_project_manager | is_site_manager)

rules.add_perm('projects.view_issue_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.add_issue_object', is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.change_issue_object', is_project_author | is_project_manager | is_project_owner | is_site_manager)  # noqa: E501
rules.add_perm('projects.delete_issue_object', is_project_manager | is_project_owner | is_site_manager)

rules.add_perm('projects.view_snapshot_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.add_snapshot_object', is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.change_snapshot_object', is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.rollback_snapshot_object', is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.export_snapshot_object', is_project_owner | is_project_manager | is_site_manager)

rules.add_perm('projects.view_value_object', is_project_member | is_visible | is_site_manager)
rules.add_perm('projects.add_value_object', is_project_author | is_project_manager | is_project_owner | is_site_manager)
rules.add_perm('projects.change_value_object', is_project_author | is_project_manager | is_project_owner | is_site_manager)  # noqa: E501
rules.add_perm('projects.delete_value_object', is_project_author | is_project_manager | is_project_owner | is_site_manager)  # noqa: E501

rules.add_perm('projects.view_page_object', is_project_member | is_visible | is_site_manager)

# TODO: use one of the permissions above
rules.add_perm('projects.is_project_owner', is_project_owner)
