from ranking.models import Player, Match, Settings, PlayerRating
from ranking.elo import Elo
from datetime import date

elo = Elo()

for discipline in ["EIGHT_BALL", 'NINE_BALL', 'TEN_BALL', 'STRAIGHT_POOL']:
    rating = {}
    num = {}
    players = Player.objects.all()
    for p in players:
        rating[p.player_id] = elo.start
        num[p.player_id] = 0

    matches = Match.objects.filter(discipline=discipline).order_by("timestamp").all()
    print(matches[0])
    for i,m in enumerate(list(matches)):
        if i % 10 == 0:
            ranking = sorted(rating.items(), key=lambda x: -x[1])
            for p, r in ranking:
                e1, e2 = elo.exp(ranking[0][1], r)
                h = round(elo.handicap(ranking[0][1], r, 5), 1)
                update = elo.update(ranking[0][1], r, 5, 5-h)
                print("{} {} {} ({} {} {} {})".format(p, int(r), num[p], e1, e2, h, update))

        p1, p2 = m.player_1_id, m.player_2_id
        s1, s2 = m.score_1, m.score_2
        s1,s2 = (0,1) if s1<s2 else (1,0)
        r1, r2 = rating[p1], rating[p2]
        update = elo.update(r1, r2, s1, s2)

        rating[p1] += update[0]
        rating[p2] += update[1]
        num[p1] += 1
        num[p2] += 1

        print(m, "value update", update)

    # TODO: Update instead of insert, whenever possible
    # TODO: Monthly ratings too
    for pid, rating in rating.items():
        if num[pid] == 0: continue
        PlayerRating.objects.create(
            player_id=pid,
            rating=int(round(rating)),
            period='ALL_TIME',
            num_matches=num[pid],
            discipline=discipline,
            month=date.today()
        )
