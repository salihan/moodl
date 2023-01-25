import pandas as pd
from sqlalchemy import create_engine
import panel as pn
import hvplot.pandas

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

# Execute the query
query = """
SELECT c.fullname as course_name, l.courseid as course_id, COUNT(DISTINCT l.userid) as student_count, COUNT(DISTINCT l.contextinstanceid) as activity_count, SEC_TO_TIME(SUM(UNIX_TIMESTAMP() - l.timecreated)) as duration 
FROM mdl_logstore_standard_log l JOIN mdl_course c ON l.courseid = c.id 
WHERE l.action = 'viewed' 
GROUP BY l.courseid 
ORDER BY student_count DESC
"""

if 'data' not in pn.state.cache.keys():
    df = pd.read_sql(query, engine)
    pn.state.cache['data'] = df.copy()
else:
    df = pn.state.cache['data']

# Create a bar chart of student count per course
# barchart = df.hvplot.bar(x='course_name', y='student_count', title='Number of students per course', rot=90)
barchart = df.hvplot.bar(x='course_id', y='student_count', title = 'Number of students per course')

# Create a table with more detailed information
# table = pn.widgets.DataFrame(df, layout='fit_columns')
table = pn.pane.DataFrame(df, width=800, escape=False, index=False)

# Card of students
pn.Card(
    pn.indicators.Number(value=42, default_color='white', name='Completion', format='{value}%'),
    hide_header=True,
    width=160
)

# # Create a Panel
# panel = pn.panel(col, template=pn.template.FastListTemplate)
#
# # Show the panel
# panel.show()

template = pn.template.FastListTemplate(
    site="Cassmile", title="Student-Courses Analysis",
    # sidebar=[pn.pane.Markdown("## Settings"), multi_select],
    # main=[pn.pane.HoloViews(table + hv.DynamicMap(cosine), sizing_mode="stretch_both")]
    main=[pn.Row(pn.Column(table)),
          pn.Row(pn.pane.HoloViews(barchart), sizing_mode = 'stretch_width')]
)
template.servable();