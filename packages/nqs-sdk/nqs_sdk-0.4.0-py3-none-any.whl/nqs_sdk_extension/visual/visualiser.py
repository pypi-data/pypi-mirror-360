import copy
from datetime import datetime


class Visualiser:
    def __init__(self, all_obs: dict[str, dict[str, list]], max_timestamp: int):
        self.all_obs = copy.deepcopy(all_obs)
        self.max_timestamp = max_timestamp

    def make_plots_observables(self) -> None:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=["Interactive Plot"])

        for metric, dict_values in self.all_obs.items():
            y = dict_values["block_timestamps"]
            x = dict_values["values"]
            if len(y) == 0:
                continue
            if y[-1] < self.max_timestamp:
                # propagate last know value
                x.append(x[-1])
                y.append(self.max_timestamp)
                # convert epoch ts to readable
            y = [datetime.utcfromtimestamp(ts) for ts in y]
            trace = go.Scatter(x=y, y=x, mode="lines+markers", line_shape="hv", name=metric)
            fig.add_trace(trace)

        # Create dropdown menu for selecting columns
        button_list = [
            {
                "label": "All Columns",
                "method": "update",
                "args": [{"visible": [True] * len(self.all_obs)}, {"title": "All Columns"}],
            }
        ] + [
            {
                "label": column,
                "method": "update",
                "args": [{"visible": [col == column for col in self.all_obs.keys()]}, {"title": column}],
            }
            for column in self.all_obs.keys()
        ]

        fig.update_layout(
            updatemenus=[{"buttons": button_list}],
            title="Interactive Plot with Column Selection",
            showlegend=True,
        )

        fig.show()
