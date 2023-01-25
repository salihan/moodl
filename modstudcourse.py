import pandas as pd
import pymysql
from panel import Column, Row, widgets
import hvplot.pandas
import panel as pn
pn.extension('tabulator')

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

# cache data to improve dashboard performance
if 'data' not in pn.state.cache.keys():
    df = pd.read_sql(query, connection)
    pn.state.cache['data'] = df.copy()
else:
    df = pn.state.cache['data']

# Save the data in a CSV file
df.to_csv('students_per_course.csv', index=False)
# print(df['id'].to_string(index=False))

# Make DataFrame Pipeline Interactive
idf = df.interactive()

# Radio buttons for Course measures by id
courseidgroup = pn.widgets.RadioButtonGroup(
    name='Course ID',
    options=df['id'].tolist(),
    button_type='success'
)

multi_select = pn.widgets.MultiSelect(name='Course ID', value=df['id'].tolist(),
    options=df['id'].tolist(), size=5)

# Create a RadioButtonGroup widget to select courses
# radiogroup = pn.widgets.RadioButtonGroup(name='Select Course', options=df['course_name'].unique().tolist())

# Create a bar chart from the DataFrame
def update_chart(event):
    selected_course = event.new
    filtered_df = df[df['id'].isin(selected_course)]
    bar_chart.object = filtered_df.hvplot.bar(x='course_name', y='student_count', width=600, height=400, title = 'Number of students per course')
    table.object = pn.widgets.Tabulator(filtered_df, width=600, height=400)

bar_chart = df.hvplot.bar(x='course_name', y='student_count', width=600, height=400, title = 'Number of students per course')
multi_select.param.watch(update_chart, 'value')

# Create a table from the DataFrame
# table = df.hvplot.table(columns=['course_name', 'student_count'], width=600, height=400)
table = pn.widgets.Tabulator(df, layout='fit_data_stretch')
multi_select.param.watch(update_chart, 'value')

template = pn.template.FastListTemplate(
    site="Cassmile", title="Student-Courses Analysis",
    sidebar=[pn.pane.Markdown("## Settings"), multi_select],
    # main=[pn.pane.HoloViews(table + hv.DynamicMap(cosine), sizing_mode="stretch_both")]
    main=[pn.Row(pn.Column(table)),
          pn.Row(pn.pane.HoloViews(bar_chart), sizing_mode = 'stretch_width')]
)
template.servable();


# # Create a sidebar layout containing the RadioButtonGroup widget
# sidebar = Column(multi_select, width=200)
#
# # Create a responsive dashboard layout
# dashboard = Row(table, sidebar, bar_chart)
#
# # Render the dashboard
# dashboard.servable()
