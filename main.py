# IMPORTS
import datetime
from bokeh.layouts import row, column, layout
from bokeh.plotting import figure, show, curdoc
from bokeh.models import ColumnDataSource, DateSlider, MultiChoice, Legend
from bokeh.models.widgets import Div
from config import *
import json 
import os
import pandas as pd
import numpy as np

# JSON DATA IMPORT
data = {}
for file in sorted(os.listdir(DATA_DIR)):
    if file.endswith(".json"):
        with open(os.path.join(DATA_DIR, file), "r") as f:
            data[os.path.splitext(file)[0]] = json.load(f)
            print("Loaded JSON file: ", file)

# DATA PRE-PROCESSING
dfs = {}
for _date, json_data in data.items():
    df = pd.DataFrame(json_data)
    for col in df.columns:
        df[col] = df[col].sort_values(key=lambda x: x.apply(lambda x: x['team']), ignore_index=True)
        df["team_id"] = df[col].apply(lambda x: x['team'])
        df[col] = df[col].apply(lambda x: x['value'])
    df.set_index("team_id", inplace=True)
    df = df.apply(pd.to_numeric)
    dfs[_date] = df
    print("Pre-processed JSON data for date: ", _date)


# DATA VISUALIZATION
## DESCRIPTION
description = Div(text=APP_TITLE)

## FUNCTIONS
def update_source(date, exclude_kpis = []):
    source_dict = dict(
        date=dates, 
        team_id= dfs[date].index, 
        scores=dfs[date]["scores"],
        wacc=dfs[date]["wacc"], 
        factory_utilization=dfs[date]["factory_utilization"],
        employee_engagement=dfs[date]["employee_engagement"],
        interest_coverage=dfs[date]["interest_coverage"],
        marketing_spend_rev=dfs[date]["marketing_spend_rev"],
        e_cars_sales=dfs[date]["e_cars_sales"],
        co2_penalty=dfs[date]["co2_penalty"],
    )
    for kpi in exclude_kpis:
        source_dict[kpi] = np.zeros(len(TEAM_NAMES))
    return source_dict

def update_plot(attr, old, new):
    print('Slider value: ', slider.value, '- selected KPIs: ', kpi_selector.value)
    date_value = pd.to_datetime(slider.value_as_date).strftime('%Y-%m-%d')
    kpi_values = kpi_selector.value
    print('Slider value: ', date_value, '- selected KPIs: ', kpi_values)
    if date_value in dfs:
        exclude_kpis = [kpi for kpi in KPIS if kpi not in kpi_values]
        source_dict = update_source(date_value, exclude_kpis)
        source.data = source_dict
    else:
        print("No data for date: ", date_value)
        zeros = np.zeros(len(TEAM_NAMES))
        source.data = dict(date=dates, team_id=TEAM_NAMES, scores=zeros)

## PLOT SETUP
dates = np.array(list(dfs.keys()), dtype=np.datetime64)
date = list(dfs.keys())[0]
source = ColumnDataSource(data=update_source(date))

## CONTROLS
slider = DateSlider(title='Date', start=dates[0], end=dates[-1], step=1, value=dates[0])
slider.on_change('value', update_plot)
kpi_selector = MultiChoice(title="KPIs", value=list(KPIS.keys()), options=list(KPIS.keys()), solid=False)
kpi_selector.on_change('value', update_plot)

## PLOTS
main_legend = []
side_legend = []
kpi_plot = figure(width=MAIN_PLOT_WIDTH, height=MAIN_PLOT_HEIGHT, x_range=TEAM_NAMES, title=MAIN_PLOT_TITLE)
for kpi in KPIS:
    color = KPIS[kpi][1]
    c1 = kpi_plot.line(x='team_id', y=kpi, source=source, color=color, alpha=0.8, line_width=4)
    c2 = kpi_plot.scatter(x='team_id', y=kpi, source=source, color=color, size=8)
    main_legend.append((KPIS[kpi][0], [c1, c2]))

kpi_plot.background_fill_color = PLOT_BACKGROUND_COLOR
kpi_plot.y_range.start = 0
kpi_plot.xaxis.major_label_orientation = 1
kpi_legend = Legend(items=main_legend)
kpi_plot.add_layout(kpi_legend, 'right')
kpi_legend.title = LEGEND_TITLE
kpi_legend.click_policy="mute"

percentage_kpis = ["wacc", "factory_utilization", "employee_engagement", "interest_coverage"]
percentage_kpi_plot = figure(width=SIDE_PLOT_WIDTH, height=SIDE_PLOT_HEIGHT, x_range=TEAM_NAMES, title=SIDE_PLOT_TITLE)
for kpi in percentage_kpis:
    color = KPIS[kpi][1]
    c1 = percentage_kpi_plot.line(x='team_id', y=kpi, source=source, color=color, alpha=0.8, width=0.8, line_width=4)
    c2 = percentage_kpi_plot.scatter(x='team_id', y=kpi, source=source, color=color, size=8)
    side_legend.append((KPIS[kpi][0], [c1, c2]))

percentage_kpi_plot.background_fill_color = PLOT_BACKGROUND_COLOR
percentage_kpi_plot.y_range.start = 0
percentage_kpi_plot.xaxis.major_label_orientation = 1
percentage_kpi_legend = Legend(items=side_legend)
percentage_kpi_plot.add_layout(percentage_kpi_legend, 'right')
percentage_kpi_legend.title = LEGEND_TITLE
percentage_kpi_legend.click_policy="mute"


# LAYOUT
layout = layout([
    row([description], sizing_mode='fixed'),
    row([slider, kpi_selector], sizing_mode='fixed'),
    [kpi_plot],
    [percentage_kpi_plot],
], sizing_mode='stretch_both')

curdoc().add_root(layout)