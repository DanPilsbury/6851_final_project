import requests
from bs4 import BeautifulSoup
import pandas as pd
import speech_recognition as sr

from old.constants import position_order, team_endpoints
from old.draw_region import display_canvas


def get_roster(team):
    print(f"getting roster for {team}")
    url = f"https://data.nba.com/data/v2022/json/mobile_teams/nba/2022/teams/{team}_roster.json"
    res = requests.get(url)
    j = res.json()
    players = j["data"]["t"]["pl"]
    return [
        {
            "name": f"{player['fn']} {player['ln']}",
            "number": player["num"],
            "pos": player["pos"],
        }
        for player in players
    ]


def get_depth_chart(team_endpoint):
    print(f"getting depth chart for {team_endpoint}")
    url = f"https://www.espn.com/nba/team/depth/_/name/{team_endpoint}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find_all("div", {"class": "nfl-depth-table"})[0]
    depth_chart = {}
    for i in range(5):
        position, row = table.find_all("tr", attrs={"data-idx": f"{i}"})
        players = row.findAll("a", attrs={"class": "AnchorLink"})
        depth_chart[position.text.strip()] = [player.text for player in players]
    return depth_chart


def get_players_depth_ranks(depth_chart):
    player_depth_ranks = {}
    for position, players in depth_chart.items():
        for i, player in enumerate(players):
            pos_rank = position_order[position]
            if player not in player_depth_ranks:
                cur_rank = float("inf"), pos_rank
            else:
                cur_rank = player_depth_ranks[player]
            new_rank = i, pos_rank
            player_depth_ranks[player] = min(new_rank, cur_rank)
    return player_depth_ranks


def get_team_roster_hrefs():
    url = f"https://www.nba.com/teams"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    teams = soup.find_all(
        "a", {"class": "Anchor_anchor__cSc3P TeamFigure_tfMainLink__OPLFu"}
    )

    team_roster_hrefs = {}
    for team in teams:
        href = team["href"].split("/")[1]
        team_roster_hrefs[team.text] = href

    return team_roster_hrefs


def get_roster_dataframe(team):
    print(f"creating dataframe for {team}")
    team_roster_hrefs = get_team_roster_hrefs()
    team_abbr = team_roster_hrefs[team]
    roster_data = get_roster(team_abbr)
    depth_chart = get_depth_chart(team_endpoints[team_abbr])
    player_ranks = get_players_depth_ranks(depth_chart)
    roster_data.sort(
        key=lambda player: player_ranks.get(
            player["name"], (float("inf"), float("inf"))
        )
    )
    return pd.DataFrame(roster_data)


def swap_players(dataframe, index1, index2):
    print(f"swapping players")
    tmp = dataframe.iloc[index1].copy()
    dataframe.iloc[index1] = dataframe.iloc[index2]
    dataframe.iloc[index2] = tmp


stats_df = pd.read_csv("data/nba-reference-per-game-2023.csv", index_col=0)


def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # read the audio data from the default microphone
        audio_data = r.record(source, duration=5)
        print("Recognizing...")
        # convert speech to text
        text = r.recognize_google(audio_data)
        print(text)
        return text


# def example_interaction():
#     state = 0
#     while True:
#         match state:
#             case 0:
#                 print("What team roster would you like to see?")
#                 team = record_audio()
#                 roster_df = get_roster_dataframe(team)
#                 print(roster_df)
#                 state = 1
#             case 1:
#                 break


# def example_interaction_voice():
#     pass


# def get_roster_command(text):
#     team = text.split("roster")[1].strip()
#     roster_df = get_roster_dataframe(team)
#     return roster_df


# def swap_players_command(text):
#     args = text.split("swap")[1].strip().split(" ")
#     index1, index2 = int(args[0]), int(args[2])
#     swap_players(roster_df, index1, index2)


# commands = {
#     "roster": get_roster_dataframe,
#     "swap": swap_players,
#     "stats": stats_df,
#     "matchups": None,
# }


# def handle_command(text, my_roster, opposing_roster=None):
#     for command, func in commands.items():
#         if command in text:
#             return func(text)


class CoachBuddy:
    def __init__(self) -> None:
        self.my_roster = get_roster_dataframe("Boston Celtics")
        self.opposing_roster = None
        self.stats = None
        self.commands = {
            "roster": self.get_roster_command,
            "swap": self.swap_players_command,
            "stats": self.get_stats_command,
            "region": self.get_region_command,
            "matchups": None,
        }

    def get_roster_command(self, text):
        team = text.split("roster")[1].strip()
        self.opposing_roster = get_roster_dataframe(team)
        return self.opposing_roster

    def swap_players_command(self, text):
        args = text.split("swap")[1].strip().split(" ")
        index1, index2 = int(args[0]), int(args[2])
        swap_players(self.my_roster, index1, index2)

    def get_stats_command(self, text):
        player = text.split("stats")[1].strip()
        self.stats = stats_df[stats_df["Player"] == player]
        return self.stats

    def get_region_command(self, text):
        display_canvas(self)

    def handle_command(self, text):
        for command, func in self.commands.items():
            if command in text:
                return func(text)

    def example_interaction_text(self):
        while True:
            command = input("Enter command:\n")
            self.handle_command(command)
            self.display_dashboard()

    def example_interaction_voice(self):
        while True:
            print("Speak Command")
            command = record_audio()
            self.handle_command(command)
            self.display_dashboard()

    def display_dashboard(self):
        print(f"updating dashboard")
        df1 = self.my_roster
        df2 = self.opposing_roster
        df3 = self.stats
        display_df = df1
        with open("display.html", mode="w") as f:
            f.write("<div> Rosters: </div>")
            if df2 is not None:
                df1["versus"] = "     "
                display_df = pd.concat(
                    [d.reset_index(drop=True) for d in [df1, df2]], axis=1
                )
            f.write(display_df.to_html())
            f.write("<br/>")
            f.write("<div> Stats: </div>")
            if self.stats is not None:
                f.write(df3.to_html())
            else:
                f.write("No stats to display")


# def example_region_stats():
#     display_canvas()


def display_dataframes(df1, df2=None):
    with open("display.html", "w") as f:
        if df2 is None:
            f.write(df1.to_html())
        else:
            df1["versus"] = "    "
            joined_df = pd.concat(
                [d.reset_index(drop=True) for d in [df1, df2]], axis=1
            )
            f.write(joined_df.to_html())


if __name__ == "__main__":
    # example_interaction()
    # example_region_stats()
    coach_buddy = CoachBuddy()
    coach_buddy.example_interaction_text()
    # coach_buddy.example_interaction_voice()
    pass
