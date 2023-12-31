from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from base.backend.utils.decorators import user_login_required
from base.backend.utils.utilities import get_request_data
from members.administration.members_administration import MembersAdministration


# Create your views here.

@csrf_exempt
@user_login_required
def create_member(request):
    try:
        kwargs = get_request_data(request)
        return JsonResponse(MembersAdministration().create_member(request, **kwargs))
    except Exception as e:
        return JsonResponse({'code': '200.201.500', 'message': str(e)})


@csrf_exempt
@user_login_required
def get_member(request):
    try:
        return JsonResponse(
            MembersAdministration().get_member(request, member_id=get_request_data(request).pop('member_id')))
    except Exception as e:
        return JsonResponse({'code': '200.200.500', 'message': str(e)})


@csrf_exempt
@user_login_required
def get_members(request):
    try:
        kwargs = get_request_data(request)
        return JsonResponse(MembersAdministration().get_members(request, **kwargs))
    except Exception as e:
        return JsonResponse({'code': '200.200.500', 'message': str(e)})


@csrf_exempt
@user_login_required
def update_member(request):
    try:
        kwargs = get_request_data(request)
        member_id = kwargs.pop('id')
        return JsonResponse(MembersAdministration().update_member(request, member_id=member_id, **kwargs))
    except Exception as e:
        return JsonResponse({'code': '200.200.500', 'message': str(e)})


@csrf_exempt
@user_login_required
def change_member_status(request):
    try:

        kwargs = get_request_data(request)
        print(f'delete :{kwargs}')
        member_id = kwargs.pop('id')
        return JsonResponse(
            MembersAdministration().change_member_status(request, member_id=member_id, **kwargs))
    except Exception as e:
        return JsonResponse({'code': '200.200.500', 'message': str(e)})


urlpatterns = [
    re_path(r'^create_member/$', create_member),
    re_path(r'^get_member/$', get_member),
    re_path(r'^get_members/$', get_members),
    re_path(r'^update_member/$', update_member),
    re_path(r'^change-member-status/$', change_member_status),
]
