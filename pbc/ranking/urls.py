from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("matches/", views.matches, name="matches"),
    path("eight_ball/", views.ranking_8, name="ranking_8"),
    path("nine_ball/", views.ranking_9, name="ranking_9"),
    path("ten_ball/", views.ranking_10, name="ranking_10"),
    path("straight_pool/", views.ranking_14, name="ranking_14"),
    path("addmatch/", views.addmatch, name="addmatch"),
    path("addmatch/submit", views.addmatch, name="addmatch"),
    path("addmatch/presubmit", views.presubmitmatch, name="presubmit"),
]
