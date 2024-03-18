# KPI Data Visualiser Demo

## Installation

I recommend creating a [conda](https://conda.io/docs/user-guide/install/) environment for the project:

`conda create -n kpi_vis_01 python=3.9`

Then activate the newly-created environment:

`conda create -n kpi_vis_01 python=3.9`

You can install prerequisite packages using pip:

`pip install -r requirements.txt`

Make sure put the data in place before running the code (i.e., in `../wbs_data`)

Then run the project using:

`bokeh serve --show main.py`

Then you should be able to access the web app locally at `http://localhost:5006/main`. Please get in touch if you face any issues at running the code.