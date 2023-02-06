import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from sqlalchemy import create_engine

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

q1 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
WHERE action = 'loggedin'
GROUP BY log_date;
"""
df = pd.read_sql_query(q1, engine)

date_range = df["log_date"].unique()
start_date = min(date_range)
end_date = max(date_range)

# print(start_date)
# print(end_date)

# Create a plotly line chart to display the login data
fig = px.line(df, x='log_date', y='log_count', title='User Login Activity')

# Add a slider to the plotly chart to allow the user to set the date range
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="1 month",
                    method="relayout",
                    args=[{"xaxis.range": ["2022-12-01", "2023-01-01"]}],
                ),
                dict(
                    label="3 months",
                    method="relayout",
                    args=[{"xaxis.range": ["2022-11-01", "2023-02-01"]}],
                ),
                dict(
                    label="6 months",
                    method="relayout",
                    args=[{"xaxis.range": ["2022-08-01", "2023-02-01"]}],
                ),
                dict(
                    label="1 year",
                    method="relayout",
                    args=[{"xaxis.range": ["2022-02-01", "2023-02-01"]}],
                ),
                dict(
                    label="All",
                    method="relayout",
                    args=[{"xaxis.autorange": True}],
                ),
            ]
        ),
    ]
)

# Show the dashboard
fig.show()
