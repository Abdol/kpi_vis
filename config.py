DATA_DIR = "../wbs_data"
UNITS = {
    "wacc": "%",
    "scores": "",
    "factory_utilization": "%",
    "employee_engagement": "%",
    "interest_coverage": "x",
    "marketing_spend_rev": " USD",
    "e_cars_sales": " units",
    "co2_penalty": "M (USD)",
}
KPIS = {
    "wacc": ("WACC", "#CC6677"),
    "scores": ("Scores", "#332288"),
    "factory_utilization": ("Factory Utilization", "#DDCC77"),
    "employee_engagement": ("Employee Engagement", "#117733"),
    "interest_coverage": ("Interest Coverage", "#88CCEE"),
    "marketing_spend_rev": ("Cumulative Marketing Spend/Rev", "#882255"),
    "e_cars_sales": ("eCars Sales", "#44AA99"),
    "co2_penalty": ("CO2 Penalty", "#999933"),
}
TEAM_NAMES = [
    "fovro",
    "Fastun",
    "Nyxx",
    "CarSpa",
    "Motion",
    "Worthwheel",
    "Carzio",
    "Rollovo",
    "iAuto",
    "VroomTime",
    "Kar",
    "EliteTechs",
    "Carz",
    "MileMode",
    "Automotiq",
    "RYDI",
    "EvolutionAuto",
    "Automovo",
    "ROBOH",
    "rimovo",
    "ottobi",
    "Evi",
    "Rusted",
    "Cjio",
    "NitroRide",
    "HXH",
    "SpeedLabs",
    "TenQ",
    "Caraxa",
    "Blazers",
    "DriveSwitch",
    "GIIQ",
    "Teuso",
    "Hoqa",
    "AutoInfinite",
    "vusk",
    "DentCenter",
    "Turbo",
    "evCU",
    "Electronically",
    "Drivat",
    "Torque",
    "Drift",
    "Carvato",
    "Rush",
    "Matic",
    "Wheelic",
    "Slidyn",
    "Pitpo",
    "caralo",
    "Drivesly",
    "Xuad",
    "CarLeap",
    "Tazox",
    "Amxu",
    "Honkli",
]
TEAMS = {}
for i in range(len(TEAM_NAMES)):
    TEAMS[i + 1] = TEAM_NAMES[i]

MAIN_PLOT_WIDTH = 1000
MAIN_PLOT_HEIGHT = 600
MAIN_PLOT_TITLE = "KPIs by Team"
SIDE_PLOT_WIDTH = 600
SIDE_PLOT_HEIGHT = 600
SIDE_PLOT_TITLE = "Percentage KPIs"
APP_TITLE = "<h1>Business in Practice | KPI Data Visualiser</h1>"
LEGEND_TITLE = "KPI (click to mute)"
PLOT_BACKGROUND_COLOR = "#EEEEEE"
