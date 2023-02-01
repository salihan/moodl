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
ORDER BY l.courseid
"""
qStudentnum = """
SELECT count(u.id) as Number_of_registered_student FROM mdl_user u 
JOIN mdl_role_assignments ra ON ra.userid = u.id JOIN mdl_context c 
ON ra.contextid = c.id JOIN mdl_role r ON ra.roleid = r.id 
WHERE c.contextlevel = 50 AND r.shortname = 'student'
"""

if 'data' not in pn.state.cache.keys():
    df = pd.read_sql(query, engine)
    pn.state.cache['data'] = df.copy()
else:
    df = pn.state.cache['data']

courses = df['course_name'].unique()
courses = ['Select'] + list(courses)
course_select = pn.widgets.Select(name='Course', options=courses, value="ALL")

idf = df.interactive()
plcourse = (idf[
        idf.course_name == course_select
    ]
    .sort_values(by='course_id')
)

# execute the query for registered students
query_registered = "SELECT COUNT(DISTINCT u.id) AS 'Number of Students' FROM mdl_user u"
result_registered = pd.read_sql(query_registered, engine)

# execute the query for enrolled students
query_enrolled = "SELECT COUNT(DISTINCT ue.userid) AS 'Number of Enrolled Students' FROM mdl_user_enrolments ue"
result_enrolled = pd.read_sql(query_enrolled, engine)#.to_string(index=False)

query_not_enrolled = "SELECT COUNT(DISTINCT u.id) AS 'Number of not Enrolled Students' FROM mdl_user u WHERE u.id NOT IN (SELECT DISTINCT ue.userid FROM mdl_user_enrolments ue)"
result_not_enrolled = pd.read_sql(query_not_enrolled, engine)#.to_string(index=False)

# execute the query for active students
query_active = """SELECT COUNT(DISTINCT u.id) as 'Number of Active Students' FROM mdl_user u 
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE u.deleted = 0 AND u.suspended = 0 AND e.status = 0
"""
result_active = pd.read_sql(query_active, engine)#.to_string(index=False)

# execute the query for inactive students
query_inactive = """SELECT COUNT(DISTINCT u.id) as 'Number of Inactive Students'
FROM mdl_user u
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE u.deleted = 0 AND u.suspended = 1 OR e.status = 1
"""
result_inactive = pd.read_sql(query_inactive, engine)#.to_string(index=False)

card = pn.Card(
    pn.indicators.Number(value=result_registered['Number of Students'].iloc[0], default_color='white',
                            name='Registered', format='{value}', font_size='45pt'),
                  background='#17A589',
                  hide_header=True,
                  width=160
              )
card2 = pn.Card(
    pn.indicators.Number(value=result_enrolled['Number of Enrolled Students'].iloc[0], default_color='white',
                            name='Enrolled', format='{value}', font_size='45pt'),
                  background='#884EA0',
                  hide_header=True,
                  width=160
              )
card3 = pn.Card(
    pn.indicators.Number(value=result_not_enrolled['Number of not Enrolled Students'].iloc[0], default_color='white',
                            name='Not Enrolled', format='{value}', font_size='45pt'),
                  background='#F5B041',
                  hide_header=True,
                  width=160
              )
card4 = pn.Card(
    pn.indicators.Number(value=result_active['Number of Active Students'].iloc[0], default_color='white',
                            name='Active', format='{value}', font_size='45pt'),
                  background='#3C8AE7',
                  hide_header=True,
                  width=160
              )
card5 = pn.Card(
    pn.indicators.Number(value=result_inactive['Number of Inactive Students'].iloc[0], default_color='white',
                            name='Inactive', format='{value}', font_size='45pt'),
                  background='#E74C3C',
                  hide_header=True,
                  width=160
              )


# Create a bar chart of student count per course
barchart = df.hvplot.bar(x='course_id', y='student_count', title = 'Number of students per course')

# Create a table with more detailed information
table = pn.pane.DataFrame(df, width=800, escape=False, index=False, theme='fast')

itable = plcourse.pipe(pn.widgets.Tabulator, pagination='remote', page_size=10, theme='fast')


template = pn.template.FastListTemplate(
    site="Cassmile", title="Student-Courses Analysis",
    sidebar=[pn.pane.Markdown("## Settings"), course_select],
    # main=[pn.pane.HoloViews(table + hv.DynamicMap(cosine), sizing_mode="stretch_both")]
    main=[pn.Row( pn.Column(card), pn.Column(card2), pn.Column(card3), pn.Column(card4), pn.Column(card5) ),
          pn.Row(pn.Column(table)),
          pn.Row(pn.pane.HoloViews(barchart), sizing_mode = 'stretch_width'),
          pn.Row(pn.Column(itable.panel()))]
)
template.servable();