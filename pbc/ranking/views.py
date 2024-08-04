from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms

from .models import Match, Player, PlayerRating, Discipline
from .elo import Elo

"""
def index(request):
    print("request")
    return HttpResponse("Hello, world. You're at the polls index.")
"""

def index(request):
    return render(request, "ranking/index.html")

def matches(request):
    # if not request.user.is_authenticated:
    #     print("User is not authenticated, redirecting...")
    #     return redirect(f"{settings.LOGIN_URL}?next={request.path}"
    match_list = Match.objects.order_by("-timestamp")
    context = {"match_list": match_list, "user_is_admin": request.user.is_staff}
    return render(request, "ranking/matches.html", context)


# TODO: Human-readable discipline string
def ranking(request, discipline):
    if not request.user.is_authenticated:
        print("Not authenticated")
        user_name = 'Anonymous'
    else:
        print("Authenticated as", request.user)
        user_name = request.user.username
    ranking_list = PlayerRating.objects.filter(discipline=discipline).order_by("-rating")
    context = {"ranking_list": ranking_list, "user_is_admin": request.user.is_staff, "discipline": discipline, 'user_name': user_name}
    return render(request, "ranking/ranking.html", context)

def ranking_8(request): return ranking(request, 'EIGHT_BALL')
def ranking_9(request): return ranking(request, 'NINE_BALL')
def ranking_10(request): return ranking(request, 'TEN_BALL')
def ranking_14(request): return ranking(request, 'STRAIGHT_POOL')

# TODO: Move to forms.py?

class AddMatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['player_1', 'player_2', 'score_1', 'score_2', 'discipline']
    # player_1 = forms.CharField(label="First player", max_length=100)

# TODO: Make it @login_required
def addmatch(request):
    context = dict()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = AddMatchForm(request.POST)
        # check whether it's valid:
        # TODO: Validate score
        # TODO: Check that two players are different
        if form.is_valid():
            print(form.cleaned_data)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect("/ranking/matches")
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Prefill player from the current user
        form = AddMatchForm(initial = {"discipline": "EIGHT_BALL"})

    context['form'] = form
    return render(request, "ranking/addmatch.html", context)

def presubmitmatch(request):
    print("Responding to presubmit")
    discipline = request._post['discipline']
    s1 = request._post['score_1']
    s2 = request._post['score_2']
    p1 = request._post['player_1']
    p2 = request._post['player_2']
    print(p1, p2, discipline, s1, s2)

    # Take ratings
    # player1 = Player.objects.filter(player_id= request._post['player_1'])
    # player2 = Player.objects.filter(player_id= request._post['player_2'])
    # print(player1, player2)
    r1 = list(PlayerRating.objects.filter(player_id=p1, period='ALL_TIME', discipline=discipline).order_by("-updated_on"))
    r2 = list(PlayerRating.objects.filter(player_id=p2, period='ALL_TIME', discipline=discipline).order_by("-updated_on"))
    # TODO: What if there are more? Pick the first one
    assert len(r1) == 1
    assert len(r2) == 1
    print(r1[0])
    print(r2[0])

    r1 = r1[0].rating
    r2 = r2[0].rating

    # Compute update for ALL_TIME variant
    elo = Elo()
    s1,s2 = (0,1) if s1<s2 else (1,0)
    up1, up2 = elo.update(r1, r2, s1, s2)
    handicap = elo.handicap(r1, r2, 5)
    data = {'current_1': r1, 'current_2': r2, 'update_1': up1, 'update_2': up2, 'handicap_race_to_5': handicap, 'handicap_to_player': p2 if r1>r2 else p1}
    print("Responding", data)
    return JsonResponse(data=data)
