import csv
from ranking.models import Player, Match

print(Player.objects.all())

"""
with open("players_2023.csv", 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        Player.objects.create(
            player_id= row["player_id"],
            display_name= row["display_name"]
        )
"""      

with open("matches_2023.csv", 'r') as file:
    reader = csv.DictReader(file)
    for i, row in enumerate(reader):
        if i <= 10: continue
        Match.objects.create(**row)
