# shiny run --reload Dashboard.py

from shiny import App, ui, render, reactive
import pandas as pd

# Daten laden
video_csv = pd.read_csv("csv.csv")

# Funktionen definieren
## Punktestand
players = ["Raphael", "Adrian "]
Punktestand = [
    (0, 22.7, {"sets": [0, 0], "points": [0, 0]}),
    (22.8, 40.5, {"sets": [0, 0], "points": [0, 15]}),
    (40.6, 59.3, {"sets": [0, 0], "points": [15, 15]}),
    (59.4, 77.3, {"sets": [0, 0], "points": [30, 15]}),
    (77.4, 97.3, {"sets": [0, 0], "points": [40, 15]}),
    (97.4, 120, {"sets": [1, 0], "points": [0, 0]}),
    (120.1, 133.3, {"sets": [1, 0], "points": [15, 0]}),
    (133.4, 145.3, {"sets": [1, 0], "points": [30, 0]}),
    (145.4, 160.2, {"sets": [1, 0], "points": [40, 0]}),
    (160.3, 178, {"sets": [2, 0], "points": [0, 0]}),
    (178.1, 207, {"sets": [2, 0], "points": [15, 0]}),
    (207.1, 244, {"sets": [2, 0], "points": [30, 0]}),
    (244.1, 267.5, {"sets": [2, 0], "points": [40, 0]}),
    (267.6, 285, {"sets": [2, 0], "points": [40, 15]}),
    (285.1, 313, {"sets": [2, 0], "points": [40, 30]}),
    (313.1, 316, {"sets": [3, 0], "points": [0, 0]}),
]

def get_current_score(current_time):
    for start_time, end_time, score_data in Punktestand:
        if start_time <= current_time < end_time:
            return score_data
    return {"sets": [0, 0], "points": [0, 0]}

# Ui definieren
app_ui = ui.page_fluid(
    ui.h1("Tennis Analyse"),
    ui.row(
        ui.column(
            6,
            ui.input_slider("time", "Videozeit (in Sekunden):", min=0, max=315, step=0.1, value=0),
            ui.HTML(
                """
                <video width="100%" height="500px" controls autoplay>
                <source src="https://drive.google.com/uc?id=1r15MI6Z11Qur6WIRnIHHQXW_Z-LecErK" type="video/mp4"> 
                Your browser does not support the video tag. 
                </video>    
                """
            ),
        ),
        ui.column(3, ui.output_ui("scoreboard")),
    ),
    ui.output_text_verbatim("info"),
)

def server(input, output, session):
    @reactive.Effect
    async def update_video_time():
        await session.send_custom_message( 
            type="set_time",
            message=input.time(),
        )

    @output
    @render.ui
    def scoreboard():
        current_time = input.time()
        score_data = get_current_score(current_time)
        sets = score_data["sets"]
        points = score_data["points"]

        return ui.HTML(
            f"""
            <style>
                .scoreboard {{
                    width: 100%;
                    border: 2px solid #000;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    margin-left: -250px;
                }}
                .scoreboard .header {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                    font-weight: bold;
                    border-bottom: 2px solid #000;
                }}
                .scoreboard .player {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                }}
                .scoreboard .player:nth-child(odd) {{
                    background-color: #e6e6e6;
                }}
                .scoreboard .name {{
                    font-weight: bold;
                }}
                .scoreboard .sets, .scoreboard .points {{
                    text-align: right;
                    width: 50px;
                }}
            </style>
            <div class="scoreboard">
                <div class="header">
                    <div class="name">Spieler</div>
                    <div class="sets">Games</div>
                    <div class="points">Punkte</div>
                </div>
                <div class="player">
                    <div class="name">{players[0]}</div>
                    <div class="sets">{sets[0]}</div>
                    <div class="points">{points[0]}</div>
                </div>
                <div class="player">
                    <div class="name">{players[1]}</div>
                    <div class="sets">{sets[1]}</div>
                    <div class="points">{points[1]}</div>
                </div>
            </div>
            """
        )

app = App(app_ui, server)
