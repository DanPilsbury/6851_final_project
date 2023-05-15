from google.cloud import bigquery
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from scipy.spatial import distance
import pickle

PROJECT_ID = "spurs-sp2018"
outcomes_dict = {
    "FGX": "Field Goal Missed",
    "FGM": "Field Goal Made",
    "TO": "Turnover",
    "PASS": "Pass",
    "BLK": "Blocked",
    "AST": "Assist",
    "VIO": "Violation",
    "FOU_S": "Shooting Foul",
}


def draw_basketball_court(fig):
    min_x = -47
    max_x = 47
    min_y = -25
    max_y = 25
    mid_x = 0
    mid_y = 0

    key_width = 19
    key_half_height = 6
    rectangles = [
        # sidelines
        (min_x, min_y, max_x, max_y),
        # key left
        (min_x, -key_half_height, min_x + key_width, key_half_height),
        # key right
        (max_x - key_width, -key_half_height, max_x, key_half_height),
        # three point line top left
        (min_x, max_y - 3, min_x + 14, max_y - 3),
        # top three point line bottom left
        (min_x, min_y + 3, min_x + 14, min_y + 3),
        # three point line top right
        (max_x - 14, max_y - 3, max_x, max_y - 3),
        # top three point line bottom right
        (max_x - 14, min_y + 3, max_x, min_y + 3),
    ]

    for rectangle in rectangles:
        fig.add_shape(
            type="rect",
            x0=rectangle[0],
            y0=rectangle[1],
            x1=rectangle[2],
            y1=rectangle[3],
            line=dict(
                color="black",
                width=2,
            ),
        )

    backboard_x_dist_from_baseline = 4
    backboard_half_width = 3
    lines = [
        # mid court line
        (mid_x, min_y, mid_x, max_y),
        # backboard left
        (
            min_x + backboard_x_dist_from_baseline,
            -backboard_half_width,
            min_x + backboard_x_dist_from_baseline,
            backboard_half_width,
        ),
        # backboard right
        (
            max_x - backboard_x_dist_from_baseline,
            -backboard_half_width,
            max_x - backboard_x_dist_from_baseline,
            backboard_half_width,
        ),
    ]
    for line in lines:
        fig.add_shape(
            type="line",
            x0=line[0],
            y0=line[1],
            x1=line[2],
            y1=line[3],
            line=dict(
                color="black",
                width=2,
            ),
        )

    hoop_radius = 0.375
    hoop_x_dist_from_baseline = 4.75
    center_circle_radius = 6

    circles = [
        # center circle
        (
            mid_x - center_circle_radius,
            mid_y - center_circle_radius,
            mid_x + center_circle_radius,
            mid_y + center_circle_radius,
        ),
        # hoop left
        (
            max_x - hoop_x_dist_from_baseline - hoop_radius,
            -hoop_radius,
            max_x - hoop_x_dist_from_baseline + hoop_radius,
            hoop_radius,
        ),
        # hoop right
        (
            min_x + hoop_x_dist_from_baseline - hoop_radius,
            -hoop_radius,
            min_x + hoop_x_dist_from_baseline + hoop_radius,
            hoop_radius,
        ),
        # free throw circle left
        (
            min_x + key_width - center_circle_radius,
            mid_y - center_circle_radius,
            min_x + key_width + center_circle_radius,
            mid_y + center_circle_radius,
        ),
        # free throw circle right
        (
            max_x - key_width - center_circle_radius,
            mid_y - center_circle_radius,
            max_x - key_width + center_circle_radius,
            mid_y + center_circle_radius,
        ),
        # (-66, 23.75, -18.5, -23.75)
    ]
    for circle in circles:
        fig.add_shape(
            type="circle",
            x0=circle[0],
            y0=circle[1],
            x1=circle[2],
            y1=circle[3],
            line=dict(
                color="black",
                width=2,
            ),
        )

    curves = [
        # left
        (-33, -22, -5, 0, -33, 22),
        # right
        (33, -22, 5, 0, 33, 22),
    ]
    for curve in curves:
        fig.add_shape(
            type="path",
            path=f"M {curve[0]},{curve[1]} Q {curve[2]},{curve[3]} {curve[4]},{curve[5]}",
            line=dict(
                color="black",
                width=2,
            ),
        )


def display_mpotion(graph_data, i=0):
    fig = get_drive_animation(graph_data, i)
    fig.show()


def get_basketball_court_fig():
    fig = px.scatter()
    draw_basketball_court(fig)
    fig.update_layout(dragmode="lasso")
    fig.update_layout(clickmode="event+select")
    fig.update_xaxes(
        scaleanchor="y",
        scaleratio=1,
    )
    fig.layout.width = 1200
    fig.layout.height = 700
    fig.update_layout(
        modebar_add=[
            "select2d",
        ]
    )
    return fig


def get_drive_animation(graph_data, i=0):
    data = graph_data[i]
    df = data["dataframe"]
    player_name = data["player_name"]
    outcomes = data["outcomes"]

    home_team = df["home_team_id"].iloc[0]
    game_id = df["game_id"].iloc[0]
    names = set(df["player_name"].unique()) - {"ball"}

    color_map = {}
    player_game_team_dict = get_player_game_team_dict()

    for name in names:
        if (name, game_id) not in player_game_team_dict:
            color_map[name] = "black"
        else:
            color_map[name] = (
                "blue" if player_game_team_dict[(name, game_id)] == home_team else "red"
            )

    color_map["ball"] = "orange"
    color_map[player_name] = "green"

    fig = px.scatter(
        df,
        x="x",
        y="y",
        animation_frame="game_clock",
        animation_group="player_name",
        hover_name="player_name",
        range_x=[-50, 50],
        range_y=[-25, 25],
        color="player_name",
        color_discrete_map=color_map,
    )

    # set the frame duration to 25
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 40

    # set the transition duration to 10
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 10

    # update fig widht and height
    fig.layout.width = 1200
    fig.layout.height = 700

    # set title of figure
    fig.layout.title = f"{player_name} Drive, outcomes: {outcomes}"

    draw_basketball_court(fig)
    fig.update_xaxes(
        scaleanchor="y",
        scaleratio=1,
    )
    fig.update_layout(dragmode="drawopenpath")
    fig.update_layout(
        modebar_add=[
            "drawopenpath",
            "eraseshape",
        ]
    )

    return fig


def get_drives_sql(season, player_name):
    drives_sql = f"""--sql
        SELECT concat(pl.firstName, ' ', pl.lastName) as player_name, bhr_outcomes, end_type, start_game_clock, end_game_clock, period, x as start_x, y as start_y, end_x, end_y, game_id, season
        from ss.drives
        join ss.players pl on pl.id = drives.ball_handler_id
        where season = '{season}'
        and concat(pl.firstName, ' ', pl.lastName) = '{player_name}'
    """
    return drives_sql


def get_drives_dataframe(season, player_name):
    bqc = bigquery.Client(project=PROJECT_ID)
    drives_sql = get_drives_sql(season, player_name)
    drives_df = bqc.query(drives_sql).to_dataframe()
    return drives_df


def get_locations_sql(game_id, start, end, period):
    locations_sql = f"""--sql
        SELECT x, y, concat(pl.firstName, ' ', pl.lastName) as player_name, game_id, player_id, season, game_clock, period, ball_x, ball_y, home_team_id
        from ss.tracking
        join ss.players as pl on pl.id = tracking.player_id
        where season in (2018, 2019)
        and game_id = '{game_id}'
        and game_clock_stopped = false
        and game_clock between {end} and {start}
        and period = {period}
    """
    return locations_sql


def get_location_data(game_id, start, end, period):
    bqc = bigquery.Client(project=PROJECT_ID)
    sql = get_locations_sql(game_id, start, end, period)
    all_data = bqc.query(sql).to_dataframe()
    return all_data


def process_location_data(all_data):
    plot_columns = [
        "x",
        "y",
        "game_clock",
        "player_name",
        "period",
        "game_id",
        "home_team_id",
    ]

    player_locations = all_data.drop_duplicates(["game_clock", "player_name", "period"])
    player_locations = player_locations.sort_values(
        by=["period", "game_clock"], ascending=[True, False]
    )
    player_locations = player_locations[plot_columns]

    ball_locations = all_data.drop_duplicates(["game_clock", "period"])
    ball_locations = ball_locations.drop(["x", "y"], axis=1)
    ball_locations = ball_locations.rename(columns={"ball_x": "x", "ball_y": "y"})
    ball_locations["player_name"] = "ball"
    ball_locations = ball_locations[plot_columns]

    all_locations = pd.concat([player_locations, ball_locations], ignore_index=True)
    all_locations = all_locations.sort_values(
        by=["period", "game_clock"], ascending=[True, False]
    ).reset_index(drop=True)
    return all_locations.fillna("unknown")


def save_player_game_team_dict():
    players_sql = """--sql
        Select concat(pl.firstName, ' ', pl.lastName) as player_name, team_id, game_id
        from ss.player_team_games
        join ss.players pl on pl.id = player_team_games.player_id
    """
    bqc = bigquery.Client(project=PROJECT_ID)
    players_df = bqc.query(players_sql).to_dataframe()

    player_game_team_dict = {}
    for index, row in players_df.iterrows():
        player_game_team_dict[(row["player_name"], row["game_id"])] = row["team_id"]

    with open("data/player_game_team.pkl", "wb") as f:
        pickle.dump(player_game_team_dict, f)

    return player_game_team_dict


def get_player_game_team_dict():
    with open("data/player_game_team.pkl", "rb") as f:
        player_game_team_dict = pickle.load(f)
    return player_game_team_dict


def get_graph_data(season, player_name, start_loc, end_loc, num_results, stat_type):
    match stat_type:
        case "drives":
            return get_drives_data(season, player_name, start_loc, end_loc, num_results)
        case "shots":
            return get_shots_fig(season, player_name, start_loc, end_loc)


def get_drives_data(season, player_name, start_loc, end_loc, num_results):
    drives_df = get_drives_dataframe(season, player_name)
    drives_df["start_dist"] = drives_df.apply(
        lambda row: distance.euclidean(start_loc, (row["start_x"], row["start_y"])),
        axis=1,
    )
    drives_df["end_dist"] = drives_df.apply(
        lambda row: distance.euclidean(end_loc, (row["end_x"], row["end_y"])), axis=1
    )
    drives_df["total_dist"] = drives_df["start_dist"] + drives_df["end_dist"]
    drives_df = drives_df.sort_values(
        by=["total_dist"], ascending=True, ignore_index=True
    )

    graph_data = {}
    for i in range(num_results):
        row = drives_df.iloc[i]
        start_game_clock = row["start_game_clock"] + 2
        end_game_clock = row["end_game_clock"] - 2
        period = row["period"]
        game_id = row["game_id"]
        location_data = get_location_data(
            game_id, start_game_clock, end_game_clock, period
        )
        location_data = process_location_data(location_data)

        outcomes = []
        for outcome in row["bhr_outcomes"]:
            outcomes.append(outcomes_dict.get(outcome, outcome))

        graph_data[i] = {
            "dataframe": location_data,
            "player_name": player_name,
            "outcomes": outcomes,
        }

    return graph_data


def get_shots_sql(season, player_name, x_range, y_range):
    return f"""--sql
    SELECT x, y, concat(pl.firstName, ' ', pl.lastName) as player_name, outcome, season
    from ss.shots
    join ss.players as pl on pl.id = shots.shooter_id
    where concat(pl.firstName, ' ', pl.lastName) = '{player_name}'
    and x between {x_range[0]} and {x_range[1]}
    and y between {y_range[0]} and {y_range[1]}
    """


def get_shots_dataframe(season, player_name, x_range, y_range):
    bqc = bigquery.Client(project=PROJECT_ID)
    shots_sql = get_shots_sql(season, player_name, x_range, y_range)
    return bqc.query(shots_sql).to_dataframe()


def get_shots_fig(season, player_name, start_loc, end_loc):
    x_range = min(start_loc[0], end_loc[0]), max(start_loc[0], end_loc[0])
    y_range = min(start_loc[1], end_loc[1]), max(start_loc[1], end_loc[1])
    df = get_shots_dataframe(season, player_name, x_range, y_range)
    makes = df[df["outcome"] == True].shape[0]
    shots = df.shape[0]
    fg_pct = makes / shots
    fig = px.scatter(
        df, x="x", y="y", color="outcome", hover_data=["player_name", "season"]
    )
    fig.update_layout(title=f"{player_name} FG%: {fg_pct:.2f}, {makes}/{shots}")

    fig.update_traces(marker_size=3)
    draw_basketball_court(fig)
    fig.update_layout(dragmode="select")
    return fig
