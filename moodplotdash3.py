import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import pymysql

# Connect to the Moodle database
conn = pymysql.connect(host="localhost", user="root", password="", db="moodle")
cursor = conn.cursor()

# Retrieve the data from the database
query = "SELECT c.id as activity_id, c.shortname as activity_name, FROM_UNIXTIME(c.startdate) as start_date, FROM_UNIXTIME(c.enddate) as end_date, COUNT(DISTINCT ue.userid) as student_count, SUM(ue.timespend) as time_spent FROM mdl_user_enrolments ue JOIN mdl_enrol e ON ue.enrolid = e.id JOIN mdl_course c ON e.courseid = c.id GROUP BY c.id"
cursor.execute(query)
data = cursor.fetchall()

# Create the DataFrame
df = pd.DataFrame(data, columns=["activity_id", "activity_name", "start_date", "end_date", "student_count", "time_spent"])

# Close the database connection
cursor.close()
conn.close()

# Create the Dash app
app = dash.Dash()

# Create the dropdown component to select activities
activity_options = []
for activity in df['activity_name'].unique():
    activity_options.append({'label':activity, 'value':activity})

# Create the layout
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='activity-select',
            options=activity_options,
            value=[activity_options[0]['value']],
            multi=True
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='activity-student-count-bar-chart'),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='time-spent-scatter-plot'),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='time-spent-histogram'),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='activity-completion-rate-bar-chart')
    ], style={'width': '48%', 'display': 'inline-block'}),
])

# Create the callback function to update the graphs
@app.callback(
    [
        Output('activity-student-count-bar-chart', 'figure'),
        Output('time-spent-scatter-plot', 'figure'),
        Output('time-spent-histogram', 'figure'),
        Output('activity-completion-rate-bar-chart', 'figure')
    ],
    [Input('activity-select', 'value')],
    state=[State('activity-select', 'value')],
    timeout=10000
)
def update_graphs(activity_name):
    filtered_df = df[df['activity_name'].isin(activity_name)]
    # Create the bar chart for student count
    bar_chart = go.Bar(x=filtered_df['activity_name'], y=filtered_df['student_count'])
    # Create the scatter plot for time spent
    scatter_plot = go.Scatter(x=filtered_df['activity_name'], y=filtered_df['time_spent'], mode='markers')
    # Create the histogram for time spent
    histogram = go.Histogram(x=filtered_df['time_spent'])
    # Create the bar chart for completion rate
    completion_rate = filtered_df['student_count'] / filtered_df['time_spent']
    completion_bar = go.Bar(x=filtered_df['activity_name'], y=completion_rate)
    return bar_chart, scatter_plot, histogram, completion_bar

if __name__ == '__main__':
    app.run_server(debug=True)
