import plotly.graph_objects as go  # or plotly.express as px
import plotly.express as px

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import json
from textwrap import dedent as d
import speech_recognition as sr

from helpers import *

DEMO_MODE = True


def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # read the audio data from the default microphone
        print("Listening...")
        audio_data = r.record(source, duration=4)
        print("Recognizing...")
        # convert speech to text
        text = r.recognize_google(audio_data)
        print(text)
        return text


def get_updated_traces(x, y):
    neg_x = [-x for x in x]
    neg_y = [-y for y in y]

    trace_1 = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color="gray", dash="dash"),
        showlegend=False,
    )
    trace_2 = go.Scatter(
        x=neg_x,
        y=neg_y,
        mode="lines",
        line=dict(color="gray", dash="dash"),
        showlegend=False,
    )
    return (trace_1, trace_2)


app = dash.Dash()

fig = get_basketball_court_fig()

# global state
graph_data = None
play_index = 0
current_traces = (None, None)
args = {
    "season": 2018,
    "player_name": "Stephen Curry",
    "start_loc": (-40, -22),
    "end_loc": (-40, 0),
    "num_results": 5,
    "stat_type": "drives",
}

play_index_options = [{"label": str(i), "value": i} for i in range(args["num_results"])]
stat_type_options = [
    {"label": "Shots", "value": "shots"},
    {"label": "Drives", "value": "drives"},
]

app.layout = html.Div(
    [
        html.H1("Coaching Buddy"),
        html.Button("Record", id="button-record"),
        html.Div(
            [
                dcc.Input(
                    id="input-player",
                    type="text",
                    placeholder="Player name",
                ),
            ]
        ),
        dcc.Dropdown(
            id="dropdown-stat-type",
            options=stat_type_options,
            placeholder="Select stat type",
        ),
        dcc.Graph(id="graph-court", figure=fig),
        html.Button("Reset", id="button-reset"),
        dcc.Dropdown(
            id="dropdown-play-index",
            options=play_index_options,
            placeholder="Select Play",
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    [
                        dcc.Markdown(d("""Debug output""")),
                        html.Pre(
                            id="debug_output",
                        ),
                    ],
                    className="three columns",
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("graph-court", "figure", allow_duplicate=True),
    Input("dropdown-stat-type", "value"),
    prevent_initial_call=True,
)
def update_stat_type(value):
    global stat_type
    args["stat_type"] = value
    global fig
    fig = get_basketball_court_fig()
    match value:
        case "shots":
            fig.update_layout(dragmode="select")
        case "drives":
            fig.update_layout(dragmode="lasso")
    return fig


@app.callback(
    Output("debug_output", "children", allow_duplicate=True),
    Output("input-player", "value"),
    Input("button-record", "n_clicks"),
    prevent_initial_call=True,
)
def record(n_clicks):
    text = record_audio()
    return text, text


@app.callback(Output("graph-court", "figure"), Input("button-reset", "n_clicks"))
def reset_graph(n_clicks):
    """
    Reset the graph to the original state
    """
    global fig
    fig = get_basketball_court_fig()
    return fig


@app.callback(
    Output("graph-court", "figure", allow_duplicate=True),
    Output("debug_output", "children"),
    Input("graph-court", "selectedData"),
    prevent_initial_call=True,
)
def display_selected_data(selectedData):
    """
    Get graph data based on selected data, and update the graph
    """
    global fig
    if selectedData and "lassoPoints" in selectedData:
        lasso_points = selectedData["lassoPoints"]
        x = lasso_points["x"]
        y = lasso_points["y"]

        args["start_loc"] = (x[0], y[0])
        args["end_loc"] = (x[-1], y[-1])

        global graph_data
        if DEMO_MODE:
            graph_data = get_demo_graph_data(
                args["stat_type"], args["start_loc"], args["end_loc"]
            )
        else:
            graph_data = get_graph_data(**args)
        fig = get_drive_animation(graph_data)

        # add a line trace for selected points
        global current_traces
        current_traces = get_updated_traces(x, y)
        for trace in current_traces:
            fig.add_trace(trace)

        return fig, json.dumps(selectedData)

    elif selectedData and "range" in selectedData:
        box_points = selectedData["range"]
        x = [box_points["x"][0], box_points["x"][1]]
        y = [box_points["y"][0], box_points["y"][1]]
        args["start_loc"] = (x[0], y[0])
        args["end_loc"] = (x[1], y[1])
        if DEMO_MODE:
            fig = get_demo_graph_data(
                args["stat_type"], args["start_loc"], args["end_loc"]
            )
        else:
            fig = get_graph_data(**args)
        # fig = get_graph_data(**args)
        # print(selectedData)
        return fig, json.dumps(selectedData)

    return fig, json.dumps(args)


@app.callback(
    Output("graph-court", "figure", allow_duplicate=True),
    Input("dropdown-play-index", "value"),
    prevent_initial_call=True,
)
def update_graph(value):
    """
    update the graph based on the selected play index
    """
    global fig
    global play_index
    play_index = value
    fig = get_drive_animation(graph_data, play_index)
    for trace in current_traces:
        fig.add_trace(trace)
    return fig


@app.callback(
    Output("graph-court", "figure", allow_duplicate=True),
    Input("input-player", "value"),
    prevent_initial_call=True,
)
def update_graph(value):
    """
    update the graph based on the selected play index
    """
    args["player_name"] = value
    global fig
    fig = get_basketball_court_fig()
    return fig


def run():
    app.run_server(debug=True, use_reloader=True)


if __name__ == "__main__":
    run()
