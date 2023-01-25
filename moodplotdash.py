import pandas as pd
import pymysql
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

# Connect to the Moodle database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='moodle'
)

# Retrieve the number of students per course
query = '''
SELECT c.id as course_id, c.fullname as course_name, FROM_UNIXTIME(c.startdate) as start_date, FROM_UNIXTIME(c.enddate) as end_date,
 COUNT(DISTINCT ue.userid) as student_count
FROM mdl_user_enrolments ue
JOIN mdl_enrol e ON ue.enrolid = e.id
JOIN mdl_course c ON e.courseid = c.id
GROUP BY c.id
'''
df = pd.read_sql(query, connection)
print(df)

# Create a Dash app
app = dash.Dash(__name__)
server = app.server

# Create a dropdown menu to select courses
# dropdown = dcc.Dropdown(
#     id='course-dropdown',
#     options=[{'label': course, 'value': course} for course in df['course_name'].unique()],
#     value=df['course_name'].unique()[0],
#     multi=True,
#     style={'width': '200px'}
# )

# Add multiselect component
multiselect = dcc.Checklist(
    id='course-multiselect',
    options=[{'label': i, 'value': i} for i in df['course_name'].unique()],
    value=df['course_name'].unique()[0],
    labelStyle={'display': 'block'}
)

# Create a bar chart from the DataFrame
def create_bar_chart(course_name):
    filtered_df = df[df['course_name'] == course_name]
    bar_chart = px.bar(filtered_df, x='course_name', y='student_count', width=600, height=400, title = 'Number of students per course')
    return bar_chart

# Create a table from the DataFrame
# def create_table(course_name):
#     filtered_df = df[df['course_name'] == course_name]
#     table = filtered_df.to_dict('records')
#     return table
# Create a table from the DataFrame

# Create a table from the DataFrame
# def create_table(course_name):
#     filtered_df = df[df['course_name'] == course_name]
#     table = dash_table.DataTable(
#         id='table',
#         columns=[{"name": i, "id": i} for i in filtered_df.columns],
#         data=filtered_df.to_dict('records'),
#         style_table={'overflowX': 'scroll'}
#     )
#     return table

def create_table(course_name):
    filtered_df = df[df['course_name'] == course_name]
    data=filtered_df.to_dict('records')
    return data



# Create the layout of the app
app.layout = html.Div([
    # html.Div([
    #     html.Div([dropdown], style={'display': 'inline-block', 'float': 'right', 'padding': '10px'}),
    # ], className='row'),
    html.Div([
        multiselect
    ], className='two columns'),
    html.Div([
        dcc.Graph(id='bar-chart'),
    ], className='six columns'),
    html.Div([
        dash_table.DataTable(id='table')
    ], className='six columns'),
    # html.Div([
    #     dcc.Graph(id='table')
    # ], className='six columns'),
], className='container')

# Update the bar chart and table when the dropdown value changes
@app.callback(
    [Output('bar-chart', 'figure'), Output('table', 'data')],
    # [Input('course-dropdown', 'value')]
    [Input('course-multiselect', 'value')]
)
# def update_chart(course_name):
#     return create_bar_chart(course_name), create_table(course_name)
# def update_chart(course_name):
#     data=create_table(course_name)
#     return create_bar_chart(course_name), data

def update_chart(course_name):
    if not isinstance(course_name, list):
        course_name = [course_name]
    data = create_table(course_name)
    return create_bar_chart(course_name), data

# Apply a theme
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
