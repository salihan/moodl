import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

q1 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
WHERE action = 'loggedin'
GROUP BY log_date;
"""
q2 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, action, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
GROUP BY log_date, action;
"""
df = pd.read_sql_query(q1, engine)
df["log_date"] = pd.to_datetime(df["log_date"])
df["log_date_unix"] = df["log_date"].apply(lambda x: x.timestamp())

start_date = df["log_date_unix"].min()
end_date = df["log_date_unix"].max()
# print(start_date)

df2 = pd.read_sql_query(q2, engine)
df2["log_date"] = pd.to_datetime(df2["log_date"])
df2["log_date_unix"] = df2["log_date"].apply(lambda x: x.timestamp())
# print(df2)

# selected_df2 = df2[(df2["log_date_unix"] >= start_date) & (df2["log_date_unix"] <= end_date)]
# print(selected_df2)

app = dash.Dash()

app.layout = html.Div([
    html.H1("User Engagement Analysis"),
    html.Div([
        dcc.RangeSlider(
            id='date-slider',
            min=start_date,
            max=end_date,
            step=1,
            value=[start_date, end_date],
            marks={
                    int(start_date): df['log_date'].min(),
                    int(end_date): df['log_date'].max()
                }
        )
    ]),
    dcc.Graph(id='user-engagement-graph'),
    dcc.Graph(id='user-action-graph')
])

@app.callback(
    Output('user-engagement-graph', 'figure'),
    Output('user-action-graph', 'figure'),
    [Input('date-slider', 'value')]
)
def update_figure(selected_dates):
    selected_df = df[(df["log_date_unix"] >= selected_dates[0]) & (df["log_date_unix"] <= selected_dates[1])]
    fig = px.bar(selected_df, x='log_date', y='log_count', title="User Engagement")
    selected_df2 = df2[(df2["log_date_unix"] >= selected_dates[0]) & (df2["log_date_unix"] <= selected_dates[1])]
    fig2 = px.bar(selected_df2, x='log_date', y='log_count', color='action', barmode='stack',
                title="User Action")
    return fig, fig2

if __name__ == '__main__':
    app.run_server(debug=True)
