import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

q1 = """
SELECT FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') AS log_date, COUNT(*) AS log_count
FROM mdl_logstore_standard_log
WHERE action = 'loggedin'
GROUP BY log_date;
"""
login_data = pd.read_sql_query(q1, engine)

date_range = login_data["log_date"].unique()
start_date = min(date_range)
end_date = max(date_range)

print(start_date)
print(end_date)

# Initialize the dashboard
app = dash.Dash()
app.layout = html.Div([
    dcc.RangeSlider(
        id='date-range-slider',
        min=login_data['log_date'].min(),
        max=login_data['log_date'].max(),
        value=[login_data['log_date'].min(), login_data['log_date'].max()],
        marks={
            str(date): str(date) for date in login_data['log_date'].unique()
        }
    ),
    dcc.Graph(id='login-count-graph')
])

# Update the graph based on the selected date range
@app.callback(
    dash.dependencies.Output('login-count-graph', 'figure'),
    [dash.dependencies.Input('date-range-slider', 'value')]
)
def update_graph(date_range):
    filtered_data = login_data[
        (login_data['log_date'] >= date_range[0]) &
        (login_data['log_date'] <= date_range[1])
    ]
    return {
        'data': [{
            'x': filtered_data['log_date'],
            'y': filtered_data['log_count'],
            'type': 'bar'
        }]
    }

if __name__ == '__main__':
    app.run_server(debug=True)
