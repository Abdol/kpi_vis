# IMPORTS
from bokeh.layouts import row, layout
from bokeh.plotting import figure, curdoc
from bokeh.models import (
    ColumnDataSource,
    DateSlider,
    MultiChoice,
    Legend,
    Dropdown,
    FactorRange,
)
from bokeh.models.widgets import Div
from bokeh.palettes import Turbo256
from bokeh.transform import linear_cmap
import ptvsd
from config import (
    APP_TITLE,
    DATA_DIR,
    KPIS,
    TEAM_NAMES,
    MAIN_PLOT_WIDTH,
    MAIN_PLOT_HEIGHT,
    MAIN_PLOT_TITLE,
    PLOT_BACKGROUND_COLOR,
    LEGEND_TITLE,
    MAIN_PLOT2_TITLE,
    LEADERBOARD_PLOT_TITLE,
    TEAMS,
    TEAMS_SORTED,
    UNITS,
)
import json
import os
import pandas as pd
import numpy as np

## FUNCTIONS
def load_json_files(dir):
    data = {}
    for file in sorted(os.listdir(dir)):
        if file.endswith(".json"):
            with open(os.path.join(DATA_DIR, file), "r") as f:
                data[os.path.splitext(file)[0]] = json.load(f)
                print("Loaded JSON file: ", file)
    return data

def make_dataframes(data):
    dfs = {}
    for _date, json_data in data.items():
        df = pd.DataFrame(json_data)
        for col in df.columns:
            df[col] = df[col].sort_values(
            key=lambda x: x.apply(lambda x: x["team"]), ignore_index=True
        )
            df["team_id"] = df[col].apply(lambda x: x["team"])
            df[col] = df[col].apply(lambda x: x["value"])
        df.set_index("team_id", inplace=True)
        df = df.apply(pd.to_numeric)
        dfs[_date] = df
        print("Pre-processed JSON data for date: ", _date)
    return dfs

def update_source(date, kpi="scores", exclude_kpis=[]):
    df = dfs[date]
    df = df.sort_values(by=kpi, ascending=False)
    global TEAMS, TEAMS_SORTED
    TEAMS_SORTED = [TEAMS[i - 1] for i in df.index]
    df = df.reset_index(names="team_id", drop=True)
    source_dict = dict(
        date=dates,
        team_id=dfs[date].index,
        team_id_sorted=df.index,
        scores=dfs[date]["scores"],
        wacc=dfs[date]["wacc"],
        factory_utilization=dfs[date]["factory_utilization"],
        employee_engagement=dfs[date]["employee_engagement"],
        interest_coverage=dfs[date]["interest_coverage"],
        marketing_spend_rev=dfs[date]["marketing_spend_rev"],
        e_cars_sales=dfs[date]["e_cars_sales"],
        co2_penalty=dfs[date]["co2_penalty"],
        kpi=df[kpi],
    )
    for _kpi in exclude_kpis:
        source_dict[_kpi] = np.zeros(len(TEAM_NAMES))
    return source_dict


def update_plot(attr, old, new):
    print("Slider value: ", slider.value, "- selected KPIs: ", kpi_selector.value)
    date_value = pd.to_datetime(slider.value_as_date).strftime("%Y-%m-%d")
    kpi_values = kpi_selector.value
    print("Slider value: ", date_value, "- selected KPIs: ", kpi_values)
    if date_value in dfs:
        exclude_kpis = [kpi for kpi in KPIS if kpi not in kpi_values]
        source_dict = update_source(date_value, exclude_kpis=exclude_kpis)
        source.data = source_dict
        leaderboard_plot.x_range.factors = [
            TEAMS_SORTED[int(team_id)] for team_id in source.data["team_id_sorted"]
        ]
    else:
        print("No data for date: ", date_value)
        zeros = np.zeros(len(TEAM_NAMES))
        source.data = dict(
            date=dates,
            team_id=TEAM_NAMES,
            scores=zeros,
            wacc=zeros,
            factory_utilization=zeros,
            employee_engagement=zeros,
            interest_coverage=zeros,
            marketing_spend_rev=zeros,
            e_cars_sales=zeros,
            co2_penalty=zeros,
            kpi=zeros,
        )


def update_leaderboard_plot(event):
    print("Leaderboard KPI: ", event.item)
    kpi = event.item
    date_value = pd.to_datetime(slider.value_as_date).strftime("%Y-%m-%d")
    exclude_kpis = [kpi for kpi in KPIS if kpi not in kpi_selector.value]
    sorted_source = update_source(date_value, kpi, exclude_kpis)
    source.data = sorted_source
    leaderboard_plot.x_range.factors = [
        TEAMS_SORTED[int(team_id)] for team_id in source.data["team_id_sorted"]
    ]
    leaderboard_plot.title.text = f"Leaderboard for {KPIS[kpi][0]} {UNITS[kpi]}"

# JSON DATA IMPORT AND PRE-PROCESSING
data = load_json_files(DATA_DIR)
dfs = make_dataframes(data)


# DATA VISUALIZATION
## DESCRIPTION
description = Div(text=APP_TITLE)


## PLOT SETUP
dates = np.array(list(dfs.keys()), dtype=np.datetime64)
date = list(dfs.keys())[0]
source = ColumnDataSource(data=update_source(date))

## CONTROLS
slider = DateSlider(title="Date", start=dates[0], end=dates[-1], step=1, value=dates[0])
slider.on_change("value", update_plot)
kpi_selector = MultiChoice(
    title="KPIs", value=list(KPIS.keys()), options=list(KPIS.keys()), solid=False
)
kpi_selector.on_change("value", update_plot)
leaderboard_kpi_selector = Dropdown(
    label="Leaderboard KPI",
    button_type="warning",
    menu=list(KPIS.keys()),
)
leaderboard_kpi_selector.on_click(update_leaderboard_plot)

## PLOTS
### LEADERBOARD PLOT
x_range = [TEAMS_SORTED[int(team_id)] for team_id in source.data["team_id_sorted"]]
x_range = FactorRange(factors=x_range)
leaderboard_plot = figure(
    width=MAIN_PLOT_WIDTH,
    height=MAIN_PLOT_HEIGHT,
    x_range=x_range,
    title=LEADERBOARD_PLOT_TITLE,
    tooltips="@$name",
)
cmap = linear_cmap(
    field_name="team_id_sorted",
    palette=Turbo256,
    low=min(source.data["team_id_sorted"]),
    high=max(source.data["team_id_sorted"]),
)
leaderboard_plot.vbar(
    x="team_id_sorted",
    top="kpi",
    name="kpi",
    width=0.8,
    source=source,
    fill_color=cmap,
    line_color="black",
)
leaderboard_plot.background_fill_color = PLOT_BACKGROUND_COLOR
leaderboard_plot.y_range.start = 0
leaderboard_plot.xaxis.major_label_orientation = 1

### MAIN KPI PLOT
main_legend = []
kpi_plot = figure(
    width=MAIN_PLOT_WIDTH,
    height=MAIN_PLOT_HEIGHT,
    x_range=TEAM_NAMES,
    title=MAIN_PLOT_TITLE,
    tooltips="@$name",
)
for kpi in KPIS:
    color = KPIS[kpi][1]
    c1 = kpi_plot.line(
        x="team_id",
        y=kpi,
        name=kpi,
        source=source,
        color=color,
        alpha=0.8,
        line_width=4,
    )
    c2 = kpi_plot.scatter(
        x="team_id", y=kpi, name=kpi, source=source, color=color, size=8
    )
    main_legend.append((KPIS[kpi][0], [c1, c2]))

kpi_plot.background_fill_color = PLOT_BACKGROUND_COLOR
kpi_plot.y_range.start = 0
kpi_plot.xaxis.major_label_orientation = 1
kpi_legend = Legend(items=main_legend)
kpi_plot.add_layout(kpi_legend, "right")
kpi_legend.title = LEGEND_TITLE
kpi_legend.click_policy = "mute"

### SECONDARY KPI PLOT
side_legend = []
percentage_kpis = [
    "wacc",
    "factory_utilization",
    "employee_engagement",
    "interest_coverage",
]
percentage_kpi_plot = figure(
    width=MAIN_PLOT_WIDTH,
    height=MAIN_PLOT_HEIGHT,
    x_range=TEAM_NAMES,
    title=MAIN_PLOT2_TITLE,
    tooltips="@$name",
)
for kpi in percentage_kpis:
    color = KPIS[kpi][1]
    c1 = percentage_kpi_plot.line(
        x="team_id",
        y=kpi,
        name=kpi,
        source=source,
        color=color,
        alpha=0.8,
        width=0.8,
        line_width=4,
    )
    c2 = percentage_kpi_plot.scatter(
        x="team_id", y=kpi, name=kpi, source=source, color=color, size=8
    )
    side_legend.append((KPIS[kpi][0], [c1, c2]))

percentage_kpi_plot.background_fill_color = PLOT_BACKGROUND_COLOR
percentage_kpi_plot.y_range.start = 0
percentage_kpi_plot.xaxis.major_label_orientation = 1
percentage_kpi_legend = Legend(items=side_legend)
percentage_kpi_plot.add_layout(percentage_kpi_legend, "right")
percentage_kpi_legend.title = LEGEND_TITLE
percentage_kpi_legend.click_policy = "mute"

# LAYOUT
layout = layout(
    [
        row([description], sizing_mode="fixed"),
        row([slider, kpi_selector], sizing_mode="fixed"),
        row([leaderboard_plot, leaderboard_kpi_selector], sizing_mode="scale_height"),
        [
            kpi_plot,
        ],
        [percentage_kpi_plot],
    ],
    sizing_mode="stretch_both",
)

# ADD TO DOCUMENT
curdoc().add_root(layout)

## DEBUGGING
if os.environ['BOKEH_VS_DEBUG'] == 'true':
    # 5678 is the default attach port in the VS Code debug configurations
    print('Waiting for debugger attach')
    ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
