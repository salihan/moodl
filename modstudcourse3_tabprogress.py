import pandas as pd
from sqlalchemy import create_engine
import panel as pn
pn.extension('tabulator')

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

# Create a table with student count column as progress type
# table = tabulator.Table(df, height=500, width=800, layout='fitData',
#                        columns=[
#                            {'title': 'Course Name', 'field': 'course_name'},
#                            {'title': 'Student Count', 'field': 'student_count', 'formatter': Progress()}
#                        ])

# table = pn.widgets.Tabulator(df, height=500,
#                              columns=[
#                                 {'title': 'Course Name', 'field': 'course_name'},
#                                 {'title': 'Student Count', 'field': 'student_count', 'formatter': 'progress'}
#                              ])


tabulator_formatters = {
    'student_count': {'type': 'progress', 'max': 10},

}
table = pn.widgets.Tabulator(df, formatters=tabulator_formatters)

template = pn.template.FastListTemplate(
    site="Cassmile", title="Student-Courses Analysis",
    # sidebar=[pn.pane.Markdown("## Settings"), multi_select],
    # main=[pn.pane.HoloViews(table + hv.DynamicMap(cosine), sizing_mode="stretch_both")]
    main=[pn.Row(pn.Column(table))]
          # pn.Row(pn.pane.HoloViews(barchart), sizing_mode = 'stretch_width')]
)
template.servable();
