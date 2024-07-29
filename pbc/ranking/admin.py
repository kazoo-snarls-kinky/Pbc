from django.contrib import admin

from .models import Player, AlternativePlayerName, Match, PlayerRating

admin.site.register(Player)
admin.site.register(AlternativePlayerName)
admin.site.register(Match)
admin.site.register(PlayerRating)

