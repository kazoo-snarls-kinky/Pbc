
from ranking.models import Settings

class Elo:
    # TODO: Add caching
    def __init__(self):
        settings = Settings.objects.filter(period="ALL_TIME").order_by("-created_on")[0]
        print('Elo settings', settings)
        self.start = settings.start_rating
        self.scaling = self.start
        self.temperature = settings.temperature

    def exp(self, r1, r2):
        e1 = 10**(r1/self.scaling)
        e2 = 10**(r2/self.scaling)
        exp1 = e1 / (e1+e2)
        exp2 = e2 / (e1+e2)
        return exp1, exp2

    def update(self, r1, r2, s1, s2):
        exp1, exp2 = self.exp(r1, r2)
        act1 = s1 / (s1+s2)
        act2 = s2 / (s1+s2)
        return self.temperature * (act1-exp1), self.temperature * (act2-exp2)

    def handicap(self, r1, r2, race_to):
# If r1 > r2 and handicap is H then, if it's a draw, then the player elo doesn't change.
# So if race_to = s1 = s2 + H then update_value(r1, r2, s1, s2) = 0
# h = x*rt
# rt / (rt + rt-xrt) = e1
# 1 / (2-x) = e1
# 2-x = 1/e1
# x = 2-1/e1
        if r1 < r2:
            r1,r2 = r2,r1
        e1, e2 = self.exp(r1, r2)
        return race_to * (2.0 - 1.0 / e1)


