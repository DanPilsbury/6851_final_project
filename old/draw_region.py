import tkinter as tk
from google.cloud import bigquery
import pandas as pd


def get_stat(self, x1, y1, x2, y2):
    print(f"region: ({x1}, {y1}) to ({x2}, {y2})")
    x1 -= 50
    x2 -= 50
    y1 -= 25
    y2 -= 25
    bqc = bigquery.Client(project="spurs-sp2018")
    tatum_id = "986b713a-b20b-4eb0-919e-c859d0508af7"
    sql = f"""
        SELECT x + 50 as x, y + 25 as y, outcome FROM ss.shots 
        WHERE shooter_id = '{tatum_id}'
        and x between {x1} and {x2}
        and y between {y1} and {y2}
        and season = '2018'
        limit 100
    """
    data = bqc.query(sql).to_dataframe()
    attempts = data.shape[0]
    makes = data["outcome"].sum()
    stats = {
        "name": "Jayson Tatum",
        "shots_attempted": attempts,
        "shots_made": makes,
        "field_goal_percentage": makes / attempts,
    }
    print(stats)
    self.stats = pd.DataFrame.from_dict(stats, orient="index").T
    return data


def display_canvas(self):
    """
    using tkinter, display a canvas that allows the user to draw a rectangle based on two mouse clicks
    the first click is the top left corner of the rectangle
    the second click is the bottom right corner of the rectangle
    """
    window = tk.Tk()
    window.title("Basketball Court")

    width = 94
    height = 50
    scale = 10
    start_x = 10
    start_y = 10

    # create a canvas
    canvas = tk.Canvas(window, width=width * scale + 20, height=height * scale + 20)
    canvas.pack()

    # draw the basketball court boundaries with dimensions times scale
    canvas.create_rectangle(
        start_x, start_y, start_x + width * scale, start_y + height * scale, fill="gray"
    )

    # draw the half court line
    canvas.create_line(
        start_x + width / 2 * scale,
        start_y,
        start_x + width / 2 * scale,
        start_y + height * scale,
        fill="white",
        width=2,
    )

    # draw a center circle with radius 6 feet
    canvas.create_oval(
        start_x + (width / 2 - 6) * scale,
        start_y + (height / 2 - 6) * scale,
        start_x + (width / 2 + 6) * scale,
        start_y + (height / 2 + 6) * scale,
        width=2,
    )

    # draw the rectangle key on the left side of the court that is 19 feet wide and 12 feet long
    canvas.create_rectangle(
        start_x,
        start_y + (height / 2 - 6) * scale,
        start_x + 19 * scale,
        start_y + (height / 2 + 6) * scale,
        width=2,
    )

    # draw the rectangle key on the right side of the court that is 19 feet wide and 12 feet long
    canvas.create_rectangle(
        start_x + width * scale,
        start_y + (height / 2 - 6) * scale,
        start_x + (width - 19) * scale,
        start_y + (height / 2 + 6) * scale,
        width=2,
    )

    # draw the free throw circle on the left side of the court with radius 6 feet that is centered 19 feet from the baseline
    canvas.create_oval(
        start_x + 19 * scale - 6 * scale,
        start_y + (height / 2 - 6) * scale,
        start_x + 19 * scale + 6 * scale,
        start_y + (height / 2 + 6) * scale,
        width=2,
    )

    # draw the free throw circle on the right side of the court with radius 6 feet that is centered 19 feet from the baseline
    canvas.create_oval(
        start_x + width * scale - 19 * scale - 6 * scale,
        start_y + (height / 2 - 6) * scale,
        start_x + width * scale - 19 * scale + 6 * scale,
        start_y + (height / 2 + 6) * scale,
        width=2,
    )

    # draw backboard on the left side of the court that is 4 feet from the baseline and 6 feet long
    canvas.create_line(
        start_x + 4 * scale,
        start_y + (height / 2 - 3) * scale,
        start_x + 4 * scale,
        start_y + (height / 2 + 3) * scale,
        width=2,
    )

    # draw backboard on the right side of the court that is 4 feet from the baseline and 6 feet long
    canvas.create_line(
        start_x + width * scale - 4 * scale,
        start_y + (height / 2 - 3) * scale,
        start_x + width * scale - 4 * scale,
        start_y + (height / 2 + 3) * scale,
        width=2,
    )

    # draw the circle hoop on the left side of the court centered 4.75 feet from the baseline and it is 0.75 inches in diameter
    canvas.create_oval(
        start_x + 4 * scale,
        start_y + (height / 2 - 0.75) * scale,
        start_x + 4 * scale + 1.5 * scale,
        start_y + (height / 2 + 0.75) * scale,
        width=2,
    )

    # draw the circle hoop on the right side of the court centered 4.75 feet from the baseline and it is 0.75 inches in diameter
    canvas.create_oval(
        start_x + width * scale - 4 * scale - 1.5 * scale,
        start_y + (height / 2 - 0.75) * scale,
        start_x + width * scale - 4 * scale,
        start_y + (height / 2 + 0.75) * scale,
        width=2,
    )

    # draw the top three point line part that is parallel to the sidelines and 14 feet long and 3 feet from the sideline
    canvas.create_line(
        start_x, start_y + 3 * scale, start_x + 14 * scale, start_y + 3 * scale, width=2
    )

    # draw the bottom three point line part that is parallel to the sidelines and 14 feet long and 3 feet from the sideline
    canvas.create_line(
        start_x,
        start_y + (height - 3) * scale,
        start_x + 14 * scale,
        start_y + (height - 3) * scale,
        width=2,
    )

    # draw the three point line arc on the left side of the court
    arc_x_0 = start_x + 4.75 * scale - 23.75 * scale
    arc_y_0 = start_y + 1.25 * scale
    arc_x_1 = start_x + 4.75 * scale + 23.75 * scale
    arc_y_1 = start_y + height * scale - 1.25 * scale
    # create an arc from arc_x_0, arc_y_0 to arc_x_1, arc_y_1
    canvas.create_arc(
        arc_x_0, arc_y_0, arc_x_1, arc_y_1, start=292, extent=136, width=2, style=tk.ARC
    )
    canvas.pack()

    # create a rectangle
    def draw_rectangle(event, events=[]):
        """
        draw a rectangle based on two mouse clicks
        the first click is the top left corner of the rectangle
        the second click is the bottom right corner of the rectangle
        """
        events.append(event)
        if len(events) == 2:
            # clear the canvas
            canvas.delete("rectangle")

            # get the coordinates of the first click
            x2, y2 = event.x, event.y
            # get the coordinates of the second click
            x1, y1 = events[0].x, events[0].y
            # draw the rectangle
            canvas.create_rectangle(x1, y1, x2, y2, tag="rectangle", outline="red")
            events.pop()
            events.pop()

            scaled_x1 = (x1 - start_x) / scale
            scaled_y1 = (y1 - start_y) / scale
            scaled_x2 = (x2 - start_x) / scale
            scaled_y2 = (y2 - start_y) / scale
            get_stat(self, scaled_x1, scaled_y1, scaled_x2, scaled_y2)

    # bind the mouse click event to the canvas
    canvas.bind("<Button-1>", draw_rectangle)
    # run the main loop
    window.mainloop()


if __name__ == "__main__":
    display_canvas()
