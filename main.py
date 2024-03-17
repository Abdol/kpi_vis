# IMPORTS
from bokeh.layouts import row
from bokeh.plotting import figure, show, curdoc
from bokeh.models import ColumnDataSource, DateSlider
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
for date, json_data in data.items():
    df = pd.DataFrame(json_data)
    for col in df.columns:
        df[col] = df[col].sort_values(key=lambda x: x.apply(lambda x: x['team']), ignore_index=True)
        df["team_id"] = df[col].apply(lambda x: x['team'])
        df[col] = df[col].apply(lambda x: x['value'])
    df.set_index("team_id", inplace=True)
    df = df.apply(pd.to_numeric)
    dfs[date] = df
    
    print("Pre-processed JSON data for date: ", date)

# DATA VISUALIZATION
dates = np.array(list(dfs.keys()), dtype=np.datetime64)
source = ColumnDataSource(data=dict(date=dates, team_id= dfs[date].index, scores=dfs[date]["scores"]))

score_plot = figure(x_range=TEAM_NAMES, title="Scores by Team")
score_plot.scatter(x='team_id', y='scores', source=source, width=0.9)
score_plot.xgrid.grid_line_color = None
score_plot.y_range.start = 0
score_plot.xaxis.major_label_orientation = 1

# Create a slider: slider
def update_plot(attr, old, new):
    date_value = slider.value_as_date.strftime('%Y-%m-%d')
    print('Slider value: ', slider.value, date_value)
    source.data = dfs[date_value]
slider = DateSlider(title='Date', start=dates[0], end=dates[-1], step=1, value=dates[0])
slider.on_change('value', update_plot)


# wacc_plot = figure(x_range=TEAM_NAMES, title="WACC by Team")
# wacc_plot.vbar(x=TEAM_NAMES, top=dfs["2023-06-19"]["wacc"], width=0.9)
# wacc_plot.xgrid.grid_line_color = None
# wacc_plot.y_range.start = 0
# score_plot.xaxis.major_label_orientation = 1
curdoc().add_root((row(score_plot, slider)))

    