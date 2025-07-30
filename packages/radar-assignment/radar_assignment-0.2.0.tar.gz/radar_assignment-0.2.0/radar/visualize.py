from typing import Protocol, Any
from dataclasses import dataclass, KW_ONLY, field

from dash import Dash, dcc, html, Input, Output

import plotly.graph_objects as go


@dataclass(frozen=True)
class Plot:
    # Data structure to hold plot configuration and data
    _: KW_ONLY
    x: list[float]
    y: list[float]
    title: str
    x_title: str
    y_title: str
    color: str

    def as_figure(self) -> go.Figure:
        # Converts Plot data to a Plotly figure for visualization
        figure = go.Figure(go.Scatter(x=self.x, y=self.y, line=dict(color=self.color)))
        figure.update_layout(
            title=self.title,
            xaxis_title=self.x_title,
            yaxis_title=self.y_title,
        )

        return figure


# Generic plotting interface for any data type T
class Plotter[T](Protocol):
    def __call__(self, data: list[T], /) -> Plot:
        """Plots the provided data in some way."""
        ...


# Called when the app is stopped
class StopListener(Protocol):
    def __call__(self) -> None:
        """Called whenever the application is stopped."""
        ...


def do_nothing() -> None:
    # Default stop listener that does nothing
    pass


@dataclass
class LiveVisualizer[T]:
    # Manages live visualization of streaming data using Dash
    plotter: Plotter[T]  # Function to generate plot from data
    collected_data: list[T] = field(init=False, default_factory=list)
    app: Dash = field(init=False)
    on_stop: StopListener = field(init=False, default=do_nothing)

    def __post_init__(self) -> None:
        # Initialize Dash app layout with plot area and control buttons
        self.app = Dash(self.__class__.__name__)
        self.app.layout = html.Div(
            children=[
                dcc.Graph(id="visualization"),
                html.Button("Stop Listening", id="stop-listening"),
                dcc.Interval(
                    id="refresh", interval=500
                ),  # Refresh every 500 ms (0.5 seconds)
            ]
        )

        # Callback to handle "Stop Listening" button click
        @self.app.callback(Input("stop-listening", "n_clicks"))
        def stop_listening(_: Any) -> None:
            self.on_stop()

        # Callback to periodically refresh the plot
        @self.app.callback(
            Output("visualization", "figure"), Input("refresh", "n_intervals")
        )
        def refresh_figure(_: Any) -> go.Figure:
            return self.plotter(self.collected_data).as_figure()

    def start(self, *, on_stop: StopListener) -> "LiveVisualizer":
        # Start the app and assign a stop listener callback
        self.on_stop = on_stop
        self.app.run()
        return self

    def update(self, data: T) -> None:
        # Append new data point to be visualized
        self.collected_data.append(data)


def create_plot(
    *,
    x: list[float],
    y: list[float],
    title: str,
    x_title: str,
    y_title: str,
    color: str,
) -> Plot:
    # Utility function to construct a Plot object
    return Plot(x=x, y=y, title=title, x_title=x_title, y_title=y_title, color=color)
