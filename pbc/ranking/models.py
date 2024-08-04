from django.db import models
import uuid
from datetime import datetime

# ---------------- Player ------------------- #

class Player(models.Model):
    # ID of the player, not changeable
    # player_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    player_id = models.CharField(max_length=128, unique=True, primary_key=True)
    # Preferred name of the player 
    display_name = models.CharField(max_length=128)
    # If filled, corresponds to authenticated user. Helps prefilling fields and allows player view.
    # If not filled, we assume player_id is the auth_user too.
    auth_user = models.CharField(max_length=128, default='', blank=True)
    language = models.CharField(max_length=2, default="DE")
    # email?
    # hidden?
    
    def __str__(self):
        return self.display_name

class AlternativePlayerName(models.Model):
    # Remove the name if player deleted
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    alt_name = models.CharField(max_length=128)

# --------------- Match --------------------- #

class Discipline(models.TextChoices):
    EIGHT_BALL = "EIGHT_BALL"
    NINE_BALL = "NINE_BALL"
    TEN_BALL = "TEN_BALL"
    STRAIGHT_POOL = "STRAIGHT_POOL"

class Match(models.Model):
    match_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    discipline = models.CharField(max_length=16, choices=Discipline)
    created_on = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=datetime.now)
    # Can't remove a player if match exists
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player1')
    player_2 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player2')
    score_1 = models.IntegerField()
    score_2 = models.IntegerField()
    hidden = models.IntegerField(default=False)
    # Currently used rating inflation, ie. increase of rating given
    # to both players. It should generally correspond to this month's settings.
    rating_inflation = models.IntegerField(default=0)
    # Liga, friendly match, tournament, ...
    context = models.CharField(max_length=128, blank=True, default='')
    comment = models.CharField(max_length=1024, blank=True, default='')

    def __str__(self):
        return "{}: {} {} - {} {} ({}, {})".format(self.timestamp, self.player_1, self.score_1, self.player_2, self.score_2, self.context, self.discipline)

# --------------- Ratings ----------------- #

class Period(models.TextChoices):
    MONTH = "MONTH"
    ALL_TIME = "ALL_TIME"

class PlayerRating(models.Model):
    # Remove the ranking if player deleted
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    period = models.CharField(max_length=16, choices=Period)
    rating = models.IntegerField()
    num_matches = models.IntegerField(default=0)
    discipline = models.CharField(max_length=16, choices=Discipline)

class Settings(models.Model):
    # The moment the setting was added. Maybe it should be tied to when it's valid
    created_on = models.DateTimeField(default=datetime.now)
    # Which period ranking it applies to
    period = models.CharField(max_length=16, choices=Period)
    rating_inflation = models.IntegerField()
    start_rating = models.IntegerField()
    temperature = models.IntegerField()

