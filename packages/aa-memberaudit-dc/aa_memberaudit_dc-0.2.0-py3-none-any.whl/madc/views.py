"""App Views"""

# Standard Library
import json

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, forms
from madc.api.helpers import get_manage_permission
from madc.models.skillchecker import SkillList

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permissions_required(["madc.basic_access"])
def index(request: WSGIRequest):
    return redirect("madc:checker", request.user.profile.main_character.character_id)


@login_required
@permissions_required(["madc.basic_access"])
def checker(request: WSGIRequest, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": _("Doctrine Checker"),
        "character_id": character_id,
        "forms": {
            "skilllist": forms.SkillListForm(),
        },
    }
    return render(request, "madc/index.html", context=context)


@login_required
@permissions_required(["madc.basic_access"])
def overview(request: WSGIRequest, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": _("Account Overview"),
        "character_id": character_id,
    }
    return render(request, "madc/admin/overview.html", context=context)


@login_required
@permissions_required(["madc.manage_access", "madc.admin_access"])
def administration(request: WSGIRequest, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": _("Doctrine Administration"),
        "character_id": character_id,
        "forms": {
            "delete": forms.DeleteForm(),
        },
    }
    return render(request, "madc/manage.html", context=context)


@login_required
@permissions_required(["madc.manage_access", "madc.admin_access"])
def doctrine(request: WSGIRequest, character_id=None):
    if character_id is None:
        character_id = request.user.profile.main_character.character_id

    context = {
        "title": _("Add Doctrine"),
        "character_id": character_id,
        "forms": {
            "skilllist": forms.SkillListForm(),
        },
    }
    return render(request, "madc/admin/add.html", context=context)


@login_required
@permissions_required(["madc.manage_access", "madc.admin_access"])
def ajax_doctrine(request: WSGIRequest):
    if request.method == "POST":
        form = forms.SkillListForm(request.POST)
        if form.is_valid():
            # skill_list = form.cleaned_data["skill_list"]
            name = form.cleaned_data["name"]
            category = form.cleaned_data["category"]
            ordering = form.cleaned_data["ordering"]

            # Get parsed skills from the form
            parsed_skills = form.get_parsed_skills()

            # Check if the skill list is empty
            if not parsed_skills:
                messages.error(
                    request, _("Your skill plan is empty. Please add skills.")
                )
                return redirect("madc:index")

            SkillList.objects.create(
                name=name,
                skill_list=json.dumps(parsed_skills, ensure_ascii=False),
                category=category,
                ordering=ordering,
            )

            messages.success(
                request,
                _("Skill plan '{}' with {} skills saved successfully.").format(
                    name, len(parsed_skills)
                ),
            )
            return redirect("madc:index")

        # Collect form errors and display them
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    error_messages.append(str(error))
                else:
                    field_label = form.fields[field].label or field
                    error_messages.append(f"{field_label}: {error}")

        if error_messages:
            messages.error(
                request,
                _("There was an error with your skill plan: ")
                + " ".join(error_messages),
            )
        else:
            messages.error(
                request,
                _(
                    "There was an error with your skill plan. Please check the form and try again."
                ),
            )
    else:
        messages.error(
            request, _("There was an error processing your request. Please try again.")
        )
    return redirect("madc:index")


@login_required
@permissions_required(["madc.manage_access", "madc.admin_access"])
@require_POST
def delete_doctrine(request: WSGIRequest):
    msg = _("Invalid Method")

    perms = get_manage_permission(
        request, request.user.profile.main_character.character_id
    )[0]
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    form = forms.DeleteForm(data=request.POST)
    if form.is_valid():
        pk = form.cleaned_data["pk"]
        skilllist_obj = SkillList.objects.get(pk=pk)
        msg = _(f"Skilllist: {skilllist_obj.name} deleted")
        msg += f" - {pk}"
        skilllist_obj.delete()
        logger.info(
            "Skilllist: %s deleted by %s", skilllist_obj.name, request.user.username
        )
        return JsonResponse(
            data={"success": True, "message": msg}, status=200, safe=False
        )
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)
