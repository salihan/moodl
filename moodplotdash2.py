import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from sqlalchemy import create_engine

# Connect to the Moodle database and retrieve the data
engine = create_engine('mysql+pymysql://root:@localhost/moodle')
query = '''SELECT c.id as course_id, c.fullname as course_name, FROM_UNIXTIME(c.startdate) as start_date, FROM_UNIXTIME(c.enddate) as end_date, 
COUNT(DISTINCT ue.userid) as student_count FROM mdl_user_enrolments ue JOIN mdl_enrol e ON ue.enrolid = e.id JOIN mdl_course c ON e.courseid = c.id GROUP BY c.id'''
df = pd.read_sql_query(query, engine)

# Create the app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create a bar chart from the DataFrame
def create_bar_chart(course_name):
    filtered_df = df[df['course_name'].isin(course_name)]
    data = [go.Bar(x=filtered_df['course_name'], y=filtered_df['student_count'])]
    layout = go.Layout(title='Number of students per course')
    figure = go.Figure(data=data, layout=layout)
    return figure

# Create the table
def create_table(course_name):
    filtered_df = df[df['course_name'].isin(course_name)]
    table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in filtered_df.columns])] +

        # Body
        [html.Tr([
            html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns
        ]) for i in range(len(filtered_df))]
    )
    return table

# Add multiselect component
multiselect = dcc.Checklist(
    id='course-multiselect',
    options=[{'label': i, 'value': i} for i in df['course_name'].unique()],
    value=[],
    labelStyle={'display': 'block'}
)

# Define the layout
app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col(multiselect, width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='bar-chart'), width=6),
            dbc.Col(html.Table(id='table'), width=6)
        ])
    ]
)

# Define the callback function
@app.callback(
    [Output('bar-chart', 'figure'), Output('table', 'children')],
    [Input('course-multiselect', 'value')]
)
def update_chart(course_name):
    if not isinstance(course_name, list):
        course_name = [course_name]
    return create_bar_chart(course_name), create_table(course_name)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

