import re
import csv
from datetime import datetime

chat = open("pbc2023.txt").read().split('\n')

re_score = re.compile("\[(.*)\].*:.*?([A-Za-z][A-Za-z\. ]+) *?[-: ] *?([A-Za-z][A-Za-z\. ]+).*? *?([0-9]+) *?[:-] *?([0-9]+)")
re_digit = re.compile("\[.*\].*:.*[0-9]+")

special_lines = {
"[17:15, 5/6/2023] Juan Pbc: Juan 75 / 48 Mario" : "Juan-Mario 75-48",
"[15:23, 5/20/2023] Beni Pbc: 75:51 Juan - Beni" : "Juan-Beni 75-51",
"[19:40, 8/29/2023] Beni Pbc: 7:2 - Beni: Bob"   : "Beni-Bob 7-2",
"[21:47, 8/29/2023] Beni Pbc: 7:4 Beni - Lionel" : "Beni-Lionel 7-4",
"[21:55, 2/2/2023] Juan Pbc: Juan  7 : 2  Karol" : "Juan-Karol 7-2",
"[18:26, 5/8/2023] Juan Pbc: Juan 75 : 28 Alf"   : "Juan-Alf 75:28",
"[18:10, 5/13/2023] Juan Pbc: Juan 75 : 62 Karol": "Juan-Karol 75:62",
"[22:07, 3/13/2023] Daniel Aerni: Beat:Daniel A. 3-5": "Beat-Daniel A 3:5"
}

map_names = {
"Daniel": "Daniel A",
"Dani": "Daniel A",
"Dani A": "Daniel A",
"Dani Aerni": "Daniel A",
"Danny": "Daniel A",
"Marta": "Martha",
"Alfred": "Alf",
"Benni": "Beni",
"Mathias": "Matthias"
}

map_discipline = {
    1: "STRAIGHT_POOL",
    2: "EIGHT_BALL",
    3: "NINE_BALL",
    4: "TEN_BALL",
    5: "STRAIGHT_POOL",
    6: "EIGHT_BALL",
    7: "NINE_BALL",
    8: "TEN_BALL",
    9: "STRAIGHT_POOL",
    10: "EIGHT_BALL",
    11: "NINE_BALL",
    12: "TEN_BALL"
}

re_missed = re.compile("(.*\].*?: )")

months_of_straight_pool = [1,5,9]

class Stats:
    def __init__(self, name):
        self.name = name
        self.games, self.wins, self.loss, self.thrill = 0, 0, 0, 0
        self.months = set()

    def game(self, name1, name2, score1, score2, month):
        is_straight_pool = month in months_of_straight_pool
        self.games += 1
        if name1 == self.name:
            if score1 > score2: self.wins += 1
            else: self.loss += 1
        if name2 == self.name:
            if score2 > score1: self.wins += 1
            else: self.loss += 1
        if abs(score1-score2) == 1 and not is_straight_pool:
            self.thrill += 1
        self.months.add(month)
        

name_list = "Karol, Alf, Bob, Mike, Mario, Beat, Stefan, Daniel A, Matthias, Lionel, Benjamin, Juan, Reto, Daniel R, Sinas, Simon, Martha, Justas, Dmitrijs, Beni".split(", ")
group_wins = "Stefan, Matthias, Beni, Lionel, Benjamin, Mario, Stefan, Bob, Stefan, Benjamin, Juan, Lionel, Karol, Beat, Beni, Bob, Mario, Alf, Beni, Bob, Mario, Simon, Beni, Karol, Justas".split(", ")
overall_wins = "Stefan, Beni, Stefan, Stefan, Juan, Karol, Beni, Mario, Beni, Mario, Beni".split(", ")
"""
"Karol": ,
"Alf": ,
"Bob": ,
"Mike": ,
"Mario": ,
"Beat": ,
"Stefan": ,
"Daniel A": ,
"Matthias": ,
"Lionel": ,
"Benjamin": ,
"Juan": ,
"Reto": ,
"Daniel R": ,
"Sinas": ,
"Simon": ,
"Martha": ,
"Justas": ,
"Dmitrijs": ,
"Beni": ,
"""

names = {}
for name in name_list:
    names[name] = Stats(name)

def to_snake(s):
    if not s: return s
    s = s[0].upper() + s[1:].lower()
    return s

def sanitize_name(s):
    if s.startswith("Liga "):
        s = s[5:]
    s = s.replace(".", "")
    s = s.strip()
    parts = s.split(' ')
    s = ' '.join(list(map(to_snake, parts)))
    if s in map_names:
        s = map_names[s]
    return s

discarded = []

with open('matches_2023.csv', 'w', newline='') as csvfile:
    # csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer = csv.DictWriter(csvfile, fieldnames=["timestamp", "player_1", "player_2", "score_1", "score_2", "discipline", "context"])
    writer.writeheader()
    for line in chat:
        if line in special_lines:
            miss = re.search(re_missed, line)
            line = miss.group(1) +  special_lines[line]
            # print("Replace: {", line, "} with {", miss.group(1), special_lines[line], "}")
        m = re.search(re_score, line)
        
        if m:
            date, name1, name2, score1, score2 = m.group(1,2,3,4,5)
            name1, name2 = sanitize_name(name1), sanitize_name(name2)
            if name1 not in names: 
                discarded.append(line)
                continue
            if name2 not in names:
                discarded.append(line)
                continue
            month = re.search(", ([0-9]+)/", date)
            if date[:3] == "24:":
                date = "00:" + date[3:]
            parsed_date = datetime.strptime(date, '%H:%M, %m/%d/%Y')
            if not month:
                discarded.append(line)
                print("Can't parse month!", line)
                continue
            month_idx = int(month.group(1))
            # print(parsed_date, name1, name2, score1, score2, map_discipline[month_idx])
            # print("{},{},{},{},{},{}".format(parsed_date, name1, name2, score1, score2, map_discipline[month_idx]))
            writer.writerow({
                'timestamp': parsed_date,
                'player_1': name1,
                'player_2': name2,
                'score_1': score1,
                'score_2': score2,
                'discipline': map_discipline[month_idx],
                'context': "Liga"
            })
                
            score1, score2 = int(score1), int(score2)
            # if score1 > 9 or score2 > 9 or max(score1,score2) < 5:
            #   print(line)
            names[name1].game(name1, name2, score1, score2, month_idx)
            names[name2].game(name1, name2, score1, score2, month_idx)
            # print(line, m.group(2))
        else:
            assert(line not in special_lines)
            if re.search("\].*:.*[0-9].*[0-9]", line):
                discarded.append(line)
                pass
                # print("With digit:", line)
        # m2 = re.search(re_digit, line)
        # if m2 and not m: print("Missed line: ", line)

print("Discarded rows:")
for row in discarded:
    print(row)

    """
    print(names.keys())
    for name, stat in names.items():
        gw = group_wins.count(name)
        ow = overall_wins.count(name)
        print(name + (' '*(10-len(name))), "{:2d} {:2d} {:2d} {:2d} {:3d} {:2d} {:2d} {:2d}".format(stat.games, stat.wins, stat.loss, stat.thrill, round(stat.wins/stat.games*100), gw, ow, len(stat.months)))

    for name in names.keys():
        print('"' + name + '": ,')
    """

# Debutants: Daniel R, Sinas, Justas, Martha, Dmitrijs
# Best win %: Stefan 75%
# Best thriller: Bob 12 41%
