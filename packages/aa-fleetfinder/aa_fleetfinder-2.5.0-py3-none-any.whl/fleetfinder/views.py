"""
Views
"""

# Third Party
from bravado.exception import HTTPNotFound

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import character_portrait_url
from allianceauth.eveonline.models import EveCharacter
from allianceauth.groupmanagement.models import AuthGroup
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Fleet Finder
from fleetfinder import __title__
from fleetfinder.models import Fleet
from fleetfinder.tasks import get_fleet_composition, open_fleet, send_fleet_invitation

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def dashboard(request):
    """
    Dashboard view

    :param request:
    :return:
    """

    context = {}

    logger.info(msg=f"Module called by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/dashboard.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def ajax_dashboard(request) -> JsonResponse:  # pylint: disable=too-many-locals
    """
    Ajax :: Dashboard information

    :param request:
    :return:
    """

    data = []
    groups = request.user.groups.all()
    fleets = (
        Fleet.objects.filter(Q(groups__group__in=groups) | Q(groups__isnull=True))
        .distinct()
        .order_by("name")
    )

    for fleet in fleets:
        fleet_commander_name = fleet.fleet_commander.character_name
        fleet_commander_portrait_url = character_portrait_url(
            character_id=fleet.fleet_commander.character_id, size=32
        )
        fleet_commander_portrait = (
            '<img class="rounded eve-character-portrait" '
            f'src="{fleet_commander_portrait_url}" '
            f'alt="{fleet_commander_name}" loading="lazy">'
        )
        fleet_commander_html = fleet_commander_portrait + fleet_commander_name

        button_join_url = reverse(
            viewname="fleetfinder:join_fleet", args=[fleet.fleet_id]
        )
        button_join_text = _("Join fleet")
        button_join = (
            f'<a href="{button_join_url}" '
            f'class="btn btn-sm btn-primary">{button_join_text}</a>'
        )

        button_details = ""
        button_edit = ""

        if request.user.has_perm(perm="fleetfinder.manage_fleets"):
            button_details_url = reverse(
                viewname="fleetfinder:fleet_details", args=[fleet.fleet_id]
            )
            button_details_text = _("View fleet details")
            button_details = (
                f'<a href="{button_details_url}" '
                f'class="btn btn-sm btn-primary">{button_details_text}</a>'
            )

            button_edit_url = reverse(
                viewname="fleetfinder:edit_fleet", args=[fleet.fleet_id]
            )
            button_edit_text = _("Edit fleet advert")
            button_edit = (
                f'<a href="{button_edit_url}" '
                f'class="btn btn-sm btn-primary">{button_edit_text}</a>'
            )

        data.append(
            {
                "fleet_commander": {
                    "html": fleet_commander_html,
                    "sort": fleet_commander_name,
                },
                "fleet_name": fleet.name,
                "created_at": fleet.created_at,
                "join": button_join,
                "details": button_details,
                "edit": button_edit,
            }
        )

    return JsonResponse(data=data, safe=False)


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
@token_required(scopes=("esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"))
def create_fleet(request, token):
    """
    Create fleet view

    :param request:
    :param token:
    :return:
    """

    context = {}

    if request.method == "POST":
        auth_groups = AuthGroup.objects.filter(internal=False).all()

        if "modified_fleet_data" in request.session:
            context["motd"] = request.session["modified_fleet_data"].get("motd", "")
            context["name"] = request.session["modified_fleet_data"].get("name", "")
            context["groups"] = request.session["modified_fleet_data"].get("groups", "")
            context["is_free_move"] = request.session["modified_fleet_data"].get(
                "free_move", ""
            )
            context["character_id"] = token.character_id
            context["auth_groups"] = auth_groups

            del request.session["modified_fleet_data"]
        else:
            context = {"character_id": token.character_id, "auth_groups": auth_groups}

        logger.info(msg=f"Fleet created by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/create-fleet.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def edit_fleet(request, fleet_id):
    """
    Fleet edit view

    :param request:
    :param fleet_id:
    :return:
    """

    fleet = Fleet.objects.get(fleet_id=fleet_id)
    auth_groups = AuthGroup.objects.filter(internal=False)

    context = {
        "character_id": fleet.fleet_commander.character_id,
        "auth_groups": auth_groups,
        "fleet": fleet,
    }

    logger.info(msg=f"Fleet {fleet_id} edit view by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/edit-fleet.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.access_fleetfinder")
def join_fleet(request, fleet_id):
    """
    Join fleet view

    :param request:
    :param fleet_id:
    :return:
    """

    context = {}
    groups = request.user.groups.all()
    fleet = Fleet.objects.filter(
        Q(groups__group__in=groups) | Q(groups=None), fleet_id=fleet_id
    ).count()

    if fleet == 0:
        return redirect(to="fleetfinder:dashboard")

    if request.method == "POST":
        character_ids = request.POST.getlist(key="character_ids", default=[])
        send_fleet_invitation.delay(character_ids=character_ids, fleet_id=fleet_id)

        return redirect(to="fleetfinder:dashboard")

    characters = (
        EveCharacter.objects.filter(character_ownership__user=request.user)
        .select_related()
        .order_by("character_name")
    )

    context["characters"] = characters

    return render(
        request=request,
        template_name="fleetfinder/join-fleet.html",
        context=context,
    )


@login_required()
@permission_required("fleetfinder.manage_fleets")
def save_fleet(request):
    """
    Save fleet

    :param request:
    :return:
    """

    if request.method == "POST":
        free_move = request.POST.get(key="free_move", default=False)

        if free_move == "on":
            free_move = True

        motd = request.POST.get(key="motd", default="")
        name = request.POST.get(key="name", default="")
        groups = request.POST.getlist(key="groups", default=[])

        try:
            open_fleet(
                character_id=request.POST["character_id"],
                motd=motd,
                free_move=free_move,
                name=name,
                groups=groups,
            )
        except HTTPNotFound as ex:
            esi_error_message = ex.swagger_result["error"]
            error_message = _(
                f"<h4>Error!</h4><p>ESI returned the following error: {esi_error_message}</p>"
            )

            messages.error(request=request, message=mark_safe(s=error_message))

            if request.POST.get(key="origin", default="") == "edit":
                return redirect(to="fleetfinder:dashboard")

            if request.POST.get(key="origin", default="") == "create":
                request.session["modified_fleet_data"] = {
                    "motd": motd,
                    "name": name,
                    "free_move": free_move,
                    "groups": groups,
                }

                return redirect(to="fleetfinder:create_fleet")

    return redirect(to="fleetfinder:dashboard")


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def fleet_details(request, fleet_id):
    """
    Fleet details view

    :param request:
    :param fleet_id:
    :return:
    """

    context = {"fleet_id": fleet_id}

    logger.info(msg=f"Fleet {fleet_id} details view called by {request.user}")

    return render(
        request=request,
        template_name="fleetfinder/fleet-details.html",
        context=context,
    )


@login_required()
@permission_required(perm="fleetfinder.manage_fleets")
def ajax_fleet_details(
    request,  # pylint: disable=unused-argument
    fleet_id,
) -> JsonResponse:
    """
    Ajax :: Fleet Details

    :param request:
    :param fleet_id:
    """

    fleet = get_fleet_composition(fleet_id)

    data = {"fleet_member": [], "fleet_composition": []}

    for member in fleet.fleet:
        data["fleet_member"].append(member)

    for ship, number in fleet.aggregate.items():
        data["fleet_composition"].append({"ship_type_name": ship, "number": number})

    return JsonResponse(data=data, safe=False)
