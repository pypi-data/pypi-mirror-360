# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI

# Django
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, providers
from madc.api import schema
from madc.api.helpers import (
    generate_button,
    get_alts_queryset,
    get_main_character,
    get_manage_permission,
)
from madc.models import SkillList

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class DoctrineCheckerApiEndpoints:
    tags = ["Doctrine Checker"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "{character_id}/doctrines/",
            response={200: list[schema.CharacterDoctrines], 403: str},
            tags=self.tags,
        )
        def get_doctrines(request, character_id: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            response, main = get_main_character(request, character_id)

            if not response:
                return 403, _("Permission Denied")

            characters = get_alts_queryset(main)

            # Get the skill lists for the main character
            skilllists = providers.skills.get_user_skill_list(
                user_id=main.character_ownership.user_id
            )

            # Active skill lists are the ones that are visible in the UI
            visibles = list(
                SkillList.objects.filter(active=1).values_list("name", flat=True)
            )

            output = {}

            for c in characters:
                output[c.character_id] = {
                    "character": c,
                    "doctrines": {},
                    "skills": {},
                }

            for k, s in skilllists["skills_list"].items():
                for k, d in s["doctrines"].items():
                    # filter out hidden items
                    if k in visibles:
                        output[s["character_id"]]["doctrines"][k] = d
                # Add skills to the character
                output[s["character_id"]]["skills"] = s["skills"]

            return list(output.values())

        @api.get(
            "administration/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def admin_doctrines(request):
            character_id = request.user.profile.main_character.character_id
            response, __ = get_manage_permission(request, character_id)

            if not response:
                return 403, _("Permission Denied")

            skilllist_obj = SkillList.objects.all().order_by("ordering", "name")

            skilllist_dict = {}

            btn_template = "madc/partials/form/button.html"
            url = reverse(
                viewname="madc:delete_doctrine",
            )

            settings_dict = {
                "title": _("Delete Skill Plan"),
                "color": "danger",
                "icon": "fa fa-trash",
                "text": _("Are you sure you want to delete this skill plan?"),
                "modal": "skillplan-delete",
                "action": url,
                "ajax": "action",
            }

            for skill_list in skilllist_obj:
                edit_btn = generate_button(
                    pk=skill_list.pk,
                    template=btn_template,
                    queryset=skilllist_obj,
                    settings=settings_dict,
                    request=request,
                )

                skilllist_dict[skill_list.name] = {
                    "name": skill_list.name,
                    "skills": skill_list.get_skills(),
                    "active": skill_list.active,
                    "ordering": skill_list.ordering,
                    "actions": {
                        "delete": format_html(edit_btn),
                    },
                }

            return skilllist_dict

        @api.get(
            "character/overview/",
            response={200: list[schema.CharacterOverview], 403: str},
            tags=self.tags,
        )
        def get_character_overview(request):
            chars_visible = SkillList.objects.visible_eve_characters(request.user)

            if chars_visible is None:
                return 403, "Permission Denied"

            chars_ids = chars_visible.values_list("character_id", flat=True)

            users_char_ids = UserProfile.objects.filter(
                main_character__isnull=False, main_character__character_id__in=chars_ids
            )

            output = []

            for character in users_char_ids:
                # pylint: disable=broad-exception-caught
                try:
                    character_data = {
                        "character_id": character.main_character.character_id,
                        "character_name": character.main_character.character_name,
                        "corporation_id": character.main_character.corporation_id,
                        "corporation_name": character.main_character.corporation_name,
                        "alliance_id": character.main_character.alliance_id,
                        "alliance_name": character.main_character.alliance_name,
                    }
                    output.append({"character": character_data})
                except AttributeError:
                    continue

            return output
