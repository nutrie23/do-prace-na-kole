from django.conf import settings # import the settings file
from models import UserAttendance

def settings_properties(request):
    return {'HEADER_COLOR': getattr(settings, 'HEADER_COLOR', "")}

def site(request):
    return {'SITE_URL': settings.SITE_URL}

def user_attendance(request):
    userprofile = request.user.userprofile
    campaign_slug = request.subdomain
    try:
        user_attendance = userprofile.userattendance_set.select_related('team__subsidiary__city', 'campaign', 'team__subsidiary__company', 't_shirt_size').get(campaign__slug=campaign_slug)
    except UserAttendance.DoesNotExist:
        user_attendance = None
    return {'user_attendance': user_attendance}
