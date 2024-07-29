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
    discipline = models.CharField(
        max_length=16,
        choices=Discipline,
        # default=YearInSchool.FRESHMAN,
    )
    # Do not add auto_now_add=True
    created_on = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=datetime.now)
    # Can't remove a player if match exists
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player1')
    player_2 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player2')
    score_1 = models.IntegerField()
    score_2 = models.IntegerField()
    hidden = models.IntegerField()
    # Currently used rating inflation, ie. increase of rating given
    # to both players. It should generally correspond to this month's settings.
    rating_inflation = models.IntegerField(default=0)
    comment = models.CharField(max_length=1024, blank=True, default='')

# --------------- Ratings ----------------- #

class PlayerRating(models.Model):
    # Remove the ranking if player deleted
    player = models.ForeignKey(Player, on_delete=models.CASCADE)


