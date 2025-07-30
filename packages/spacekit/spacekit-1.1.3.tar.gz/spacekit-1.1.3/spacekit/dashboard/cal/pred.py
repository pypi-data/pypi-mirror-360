from dash import dcc
from dash import html
import dash_cytoscape as cyto
import dash_daq as daq
from spacekit.dashboard.cal import nodegraph
from spacekit.dashboard.cal.config import ipsts


stylesheet = nodegraph.make_stylesheet()
styles = nodegraph.make_styles()
edges, nodes = nodegraph.make_neural_graph()

layout = html.Div(
    children=[
        # nav
        html.Div(
            children=[
                html.P("|", style={"display": "inline-block"}),
                dcc.Link(
                    "Home",
                    href="/",
                    style={"padding": 5, "display": "inline-block"},
                ),
                html.P("|", style={"display": "inline-block"}),
                dcc.Link(
                    "Evaluation",
                    href="/eval",
                    style={"padding": 5, "display": "inline-block"},
                ),
                html.P("|", style={"display": "inline-block"}),
                dcc.Link(
                    "Analysis",
                    href="/eda",
                    style={"padding": 10, "display": "inline-block"},
                ),
                html.P("|", style={"display": "inline-block"}),
            ],
            style={"display": "inline-block"},
        ),
        # GRAPH
        html.Div(
            children=[
                cyto.Cytoscape(
                    id="cytoscape-compound",
                    layout={"name": "preset"},
                    style={
                        "width": "99vw",
                        "height": "60vh",
                        "display": "inline-block",
                        "float": "center",
                        "background-color": "#1b1f34",
                    },
                    stylesheet=stylesheet,
                    elements=edges + nodes,
                ),
                html.Div(
                    children=[
                        html.P(id="cytoscape-tapNodeData-output", style=styles["pre"]),
                        html.P(id="cytoscape-tapEdgeData-output", style=styles["pre"]),
                        html.P(
                            id="cytoscape-mouseoverNodeData-output", style=styles["pre"]
                        ),
                        html.P(
                            id="cytoscape-mouseoverEdgeData-output", style=styles["pre"]
                        ),
                    ],
                    style={
                        "width": "100%",
                        "margin": 0,
                        "padding": 0,
                        "display": "inline-block",
                        "float": "left",
                        "background-color": "#1b1f34",
                    },
                ),
            ]
        ),
        # CONTROLS
        html.Div(
            id="controls",
            children=[
                # # INPUT DROPDOWNS
                html.Div(
                    id="x-features",
                    children=[
                        # FEATURE SELECTION DROPDOWNS (Left)
                        html.Div(
                            id="inputs-one",
                            children=[
                                html.Label(
                                    [
                                        html.Label(
                                            "IPPPSSOOT",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="select-ipst",
                                            options=[
                                                {"label": i, "value": i} for i in ipsts
                                            ],
                                            value="idio03010",
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "INSTR",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="instr-state",
                                            options=[
                                                {"label": "ACS", "value": 0},
                                                {"label": "COS", "value": 1},
                                                {"label": "STIS", "value": 2},
                                                {"label": "WFC3", "value": 3},
                                            ],
                                            value=0,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "DTYPE",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="dtype-state",
                                            options=[
                                                {"label": "SINGLETON", "value": 0},
                                                {"label": "ASSOCIATION", "value": 1},
                                            ],
                                            value=0,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "DETECTOR",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="detector-state",
                                            options=[
                                                {"label": "IR/HRC/SBC", "value": 0},
                                                {"label": "UVIS/WFC", "value": 1},
                                            ],
                                            value=0,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "SUBARRAY",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="subarray-state",
                                            options=[
                                                {"label": "TRUE", "value": 1},
                                                {"label": "FALSE", "value": 0},
                                            ],
                                            value=0,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                )
                                # END outputs Left Col
                            ],
                            style={
                                "display": "inline-block",
                                "float": "left",
                                "padding": 5,
                                "width": 270,
                            },
                        ),  # 'border': 'thin lightgrey solid',
                        # INPUTS RIGHT COL
                        html.Div(
                            id="inputs-two",
                            children=[
                                html.Label(
                                    [
                                        html.Label(
                                            "PCTECORR",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="pctecorr-state",
                                            options=[
                                                {"label": "OMIT", "value": 0},
                                                {"label": "PERFORM", "value": 1},
                                            ],
                                            value=1,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "DRIZCORR",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="drizcorr-state",
                                            options=[
                                                {"label": "OMIT", "value": 0},
                                                {"label": "PERFORM", "value": 1},
                                            ],
                                            value=1,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "CRSPLIT",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        daq.NumericInput(
                                            id="crsplit-state",
                                            value=2,
                                            min=0,
                                            max=2,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "TOTAL_MB",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        daq.NumericInput(
                                            id="totalmb-state",
                                            value=4,
                                            min=0,
                                            max=900,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                ),
                                html.Label(
                                    [
                                        html.Label(
                                            "N_FILES",
                                            style={
                                                "padding": 5,
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        ),
                                        daq.NumericInput(
                                            id="nfiles-state",
                                            value=2,
                                            min=1,
                                            max=200,
                                            style={
                                                "color": "black",
                                                "width": 135,
                                                "display": "inline-block",
                                                "float": "right",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 255,
                                    },
                                )
                                # END Input Right COL
                            ],
                            style={
                                "display": "inline-block",
                                "float": "left",
                                "padding": 5,
                                "width": 270,
                            },
                        ),  # 'border': 'thin lightgrey solid',
                        # END FEATURE INPUTS
                    ],
                    style={
                        "display": "inline-block",
                        "float": "left",
                        "paddingTop": 20,
                        "paddingBottom": 5,
                        "paddingLeft": "2.5%",
                        "paddingRight": "2.5%",
                        "background-color": "#242a44",
                        "min-height": 311,
                    },
                ),  # 'border': 'thin lightgreen solid',
                # MEMORY PRED VS ACTUAL
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Button(
                                            "PREDICT",
                                            id="submit-button-state",
                                            n_clicks=0,
                                            style={"width": 110},
                                        )
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "center",
                                        "width": 120,
                                        "paddingTop": 15,
                                        "paddingLeft": 15,
                                    },
                                ),
                                html.Div(
                                    [
                                        # Memory Bin Prediction LED Display
                                        daq.LEDDisplay(
                                            id="prediction-bin-output",
                                            # label="PRED",
                                            # labelPosition='bottom',
                                            value="0",
                                            color="#2186f4",
                                            size=64,
                                            backgroundColor="#242a44",
                                            # style={'display': 'inline-block', 'float': 'center'}
                                        )
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "center",
                                        "paddingTop": 20,
                                        "paddingBottom": 5,
                                        "paddingLeft": 30,
                                        "width": 120,
                                    },
                                ),
                                html.Div(
                                    [
                                        daq.BooleanSwitch(
                                            id="activate-button-state",
                                            on=False,
                                            label="ACTIVATE",
                                            labelPosition="bottom",
                                            color="#2186f4",
                                        )  # '#00EA64'
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "center",
                                        "width": 120,
                                        "paddingTop": 15,
                                        "paddingLeft": 10,
                                    },
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "float": "left",
                                "padding": 5,
                                "width": 140,
                            },
                        ),  # 'border': 'thin lightgrey solid',
                        # Probabilities
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        daq.GraduatedBar(
                                            id="p0",
                                            label="P(0)",
                                            labelPosition="bottom",
                                            step=0.05,
                                            min=0,
                                            max=1,
                                            value=1.0,
                                            showCurrentValue=True,
                                            vertical=True,
                                            size=220,
                                            color="rgb(33, 134, 244)",
                                            style=styles["gradbar-blue"],
                                        ),
                                        daq.GraduatedBar(
                                            id="p1",
                                            label="P(1)",
                                            labelPosition="bottom",
                                            step=0.05,
                                            min=0,
                                            max=1,
                                            value=0.30,
                                            showCurrentValue=True,
                                            vertical=True,
                                            size=220,
                                            color="rgb(33, 134, 244)",
                                            style=styles["gradbar-blue"],
                                        ),
                                        daq.GraduatedBar(
                                            id="p2",
                                            label="P(2)",
                                            labelPosition="bottom",
                                            step=0.05,
                                            min=0,
                                            max=1,
                                            value=0.60,
                                            showCurrentValue=True,
                                            vertical=True,
                                            size=220,
                                            color="rgb(33, 134, 244)",
                                            style=styles["gradbar-blue"],
                                        ),
                                        daq.GraduatedBar(
                                            id="p3",
                                            label="P(3)",
                                            labelPosition="bottom",
                                            step=0.05,
                                            min=0,
                                            max=1,
                                            value=0.10,
                                            showCurrentValue=True,
                                            vertical=True,
                                            size=220,
                                            color="rgb(33, 134, 244)",
                                            style=styles["gradbar-blue"],
                                        )
                                        # END Probabilities
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 175,
                                    },
                                )
                            ],
                            style={
                                "display": "inline-block",
                                "float": "left",
                                "padding": 5,
                                "width": 190,
                            },
                        ),  # 'border': 'thin lightgrey solid',
                    ],
                    style={
                        "display": "inline-block",
                        "float": "left",
                        "paddingTop": 5,
                        "paddingBottom": 5,
                        "paddingLeft": "2.5%",
                        "paddingRight": "2.5%",
                        "background-color": "#242a44",
                        "min-height": 326,
                    },
                ),  # 'border': 'thin lightgreen solid',
                # Memory GAUGE Predicted vs Actual
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        daq.Gauge(
                                            id="memory-gauge-predicted",
                                            color="#2186f4",  # '#00EA64',
                                            label="Memory (pred)",
                                            labelPosition="bottom",
                                            units="GB",
                                            showCurrentValue=True,
                                            max=64,
                                            min=0,
                                            size=175,
                                            style={
                                                "color": "white",
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        )
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 200,
                                    },
                                ),
                                html.Div(
                                    children=[
                                        daq.Gauge(
                                            id="wallclock-gauge-predicted",
                                            color="#2186f4",  # '#00EA64',
                                            value=4500,
                                            label="Wallclock (pred)",
                                            labelPosition="bottom",
                                            units="SECONDS",
                                            showCurrentValue=True,
                                            max=72000,
                                            min=0,
                                            size=175,
                                            style={
                                                "color": "white",
                                                "display": "inline-block",
                                                "float": "left",
                                            },
                                        )
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "float": "left",
                                        "margin": 5,
                                        "width": 200,
                                    },
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "float": "left",
                                "padding": 5,
                                "width": 440,
                            },
                        )  # 'border': 'thin lightgrey solid',
                    ],
                    style={
                        "display": "inline-block",
                        "float": "left",
                        "paddingTop": 5,
                        "paddingBottom": 5,
                        "paddingLeft": "2.5%",
                        "paddingRight": "2.5%",
                        "background-color": "#242a44",
                        "min-height": 326,
                    },
                ),  # 'border': 'thin lightgreen solid',
                # END Controls and Outputs
            ],
            style={
                "width": "100%",
                "display": "inline-block",
                "float": "center",
                "background-color": "#242a44",
            },
        )
        # PAGE LAYOUT
    ],
    style={
        "width": "100%",
        "height": "100%",
        "background-color": "#242a44",
        "color": "white",
    },
)
