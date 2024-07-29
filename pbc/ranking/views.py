from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings

from .models import Match

"""
def index(request):
    print("request")
    return HttpResponse("Hello, world. You're at the polls index.")
"""

def index(request):
    if not request.user.is_authenticated:
        print("User is not authenticated, redirecting...")
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    match_list = Match.objects.order_by("-timestamp")
    context = {"match_list": match_list, "user_is_admin": True}
    return render(request, "ranking/matches.html", context)

