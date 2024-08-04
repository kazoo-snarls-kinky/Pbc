from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings

from .models import Match, Player, PlayerRating, Discipline

"""
def index(request):
    print("request")
    return HttpResponse("Hello, world. You're at the polls index.")
"""

def index(request):
    return render(request, "ranking/index.html")

def matches(request):
    if not request.user.is_authenticated:
        print("User is not authenticated, redirecting...")
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    match_list = Match.objects.order_by("-timestamp")
    context = {"match_list": match_list, "user_is_admin": request.user.is_staff}
    return render(request, "ranking/matches.html", context)


def ranking(request, discipline):
    ranking_list = PlayerRating.objects.filter(discipline=discipline).order_by("-rating")
    context = {"ranking_list": ranking_list, "user_is_admin": request.user.is_staff, "discipline": discipline}
    return render(request, "ranking/ranking.html", context)

def ranking_8(request): return ranking(request, 'EIGHT_BALL')
def ranking_9(request): return ranking(request, 'NINE_BALL')
def ranking_10(request): return ranking(request, 'TEN_BALL')
def ranking_14(request): return ranking(request, 'STRAIGHT_POOL')
