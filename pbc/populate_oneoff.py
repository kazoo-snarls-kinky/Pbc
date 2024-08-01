from ranking.models import Match

print(Match.objects.all())

with open("matches_2023.csv", 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        Match.objects.create(
            discipline=row['discipline'],
            timestamp=datetime.strptime(row['ts'])
