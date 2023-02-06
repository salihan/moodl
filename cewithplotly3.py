import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

q1 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
WHERE action = 'loggedin'
GROUP BY log_date;
"""
df1 = pd.read_sql_query(q1, engine)

df1["log_date"] = pd.to_datetime(df1["log_date"])
df1["log_date_unix"] = df1["log_date"].apply(lambda x: x.timestamp())

start_date = df1["log_date_unix"].min()
end_date = df1["log_date_unix"].max()

q2 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, action, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
GROUP BY log_date, action;
"""
df2 = pd.read_sql_query(q2, engine)

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
                    int(start_date): df1['log_date'].min(),
                    int(end_date): df1['log_date'].max()
                }
        )
    ]),
    html.Br(),
    html.H2("User Engagement"),
    dcc.Graph(id='user-engagement-graph'),
    html.Br(),
    html.H2("Action Breakdown"),
    html.Table(id='action-breakdown-table')
])

@app.callback(
    [Output('user-engagement-graph', 'figure'),
     Output('action-breakdown-table', 'children')],
    [Input('date-slider', 'value')]
)
def update_figures(selected_dates):
    selected_df1 = df1[(df1["log_date_unix"] >= selected_dates[0]) & (df1["log_date_unix"] <= selected_dates[1])]
    selected_df2 = df2[(df1["log_date_unix"] >= selected_dates[0]) & (df1["log_date_unix"] <= selected_dates[1])]
    fig = px.bar(selected_df1, x='log_date', y='log_count', title="User Engagement")

    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in selected_df2.columns])] +

        # Body
        [html.Tr([            html.Td(selected_df2.iloc[i][col]) for col in selected_df2.columns
        ]) for i in range(len(selected_df2))]
    )

    return fig, table

if __name__ == '__main__':
    app.run_server(debug=True)

