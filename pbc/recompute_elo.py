from ranking.models import Player, Match, Settings, PlayerRating

for discipline in ["EIGHT_BALL", 'NINE_BALL', 'TEN_BALL', 'STRAIGHT_POOL']:
    settings = Settings.objects.filter(period="ALL_TIME").order_by("created_on")[0]
    START = settings.start_rating
    SCALING = START / 4
    TEMPERATURE = settings.temperature

    elo = {}
    num = {}
    players = Player.objects.all()
    for p in players:
        elo[p.player_id] = START
        num[p.player_id] = 0

    matches = Match.objects.filter(discipline=discipline).order_by("timestamp").all()
    print(matches[0])

    def update_value(r1, r2, s1, s2):
        e1 = 10**(r1/START)
        e2 = 10**(r2/START)
        exp1 = e1 / (e1+e2)
        exp2 = e2 / (e1+e2)
        act1 = s1 / (s1+s2)
        act2 = s2 / (s1+s2)
        return TEMPERATURE * (act1-exp1), TEMPERATURE * (act2-exp2)

    for i,m in enumerate(list(matches)):
        if i % 10 == 0:
            ranking = sorted(elo.items(), key=lambda x: -x[1])
            for p, s in ranking:
                print(p,int(s),num[p])

        p1, p2 = m.player_1_id, m.player_2_id
        s1, s2 = m.score_1, m.score_2
        s1,s2 = (0,1) if s1<s2 else (1,0)
        r1, r2 = elo[p1], elo[p2]
        update = update_value(r1, r2, s1, s2)

        elo[p1] += update[0]
        elo[p2] += update[1]
        num[p1] += 1
        num[p2] += 1

        print(m, "value update", update)

    for pid, rating in elo.items():
        if num[pid] == 0: continue
        PlayerRating.objects.create(
            player_id=pid,
            rating=int(round(rating)),
            period='ALL_TIME',
            num_matches=num[pid],
            discipline=discipline
        )
