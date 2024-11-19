# shiny run --reload Dashboard.py

from shiny import App, ui, render, reactive

app_ui = ui.page_fluid(
    ui.input_slider("time", "Videozeit (in Sekunden):", min=0, max=10, step=0.1, value=0),
    ui.HTML(
        """
        <video id="videoPlayer" width="100%" controls>
            <source src="static/match.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        """
    ),
    ui.output_text_verbatim("info")
)

def server(input, output, session):
    @reactive.Effect
    def update_video_time():
        session.send_custom_message(
            type="set_time",
            message=input.time(),
        )

app = App(app_ui, server)
