from google.cloud import bigquery
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from scipy.spatial import distance
import pickle

from helpers import (
    get_drives_dataframe,
    get_location_data,
    process_location_data,
    get_shots_dataframe,
    outcomes_dict,
    demo_locations,
    demo_shot_ranges,
)

season = 2018
player_name = "Kevin Durant"
num_results = 5


def save_drives_data():
    drives_df = get_drives_dataframe(season, player_name)
    drives_df.to_pickle("data/drives_dataframe_kevin_durant.pkl")
    return drives_df


def save_shots_data():
    for k, range_dict in demo_shot_ranges.items():
        x_range = range_dict["x_range"]
        y_range = range_dict["y_range"]
        shots_df = get_shots_dataframe(
            season,
            player_name,
            x_range,
            y_range,
        )
        shots_df.to_pickle(f"data/shots_dataframe_kevin_durant_{k}.pkl")

    return None


def save_graph_data():
    for k, loc_dict in demo_locations.items():
        start_loc = loc_dict["start_loc"]
        end_loc = loc_dict["end_loc"]

        drives_df = pd.read_pickle("data/drives_dataframe_kevin_durant.pkl")

        drives_df["start_dist"] = drives_df.apply(
            lambda row: distance.euclidean(start_loc, (row["start_x"], row["start_y"])),
            axis=1,
        )

        drives_df["end_dist"] = drives_df.apply(
            lambda row: distance.euclidean(end_loc, (row["end_x"], row["end_y"])),
            axis=1,
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

        # save graph_data as pickle
        with open(f"data/graph_data_{k}.pkl", "wb") as f:
            pickle.dump(graph_data, f)


if __name__ == "__main__":
    # save_drives_data()
    # save_graph_data()
    # save_shots_data()
    pass
