import pandas as pd
from sqlalchemy import create_engine
import panel as pn
import hvplot.pandas

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

# SQL queries
query_users = "SELECT COUNT(*) as 'Number of Users' FROM mdl_user"
query_courses = "SELECT COUNT(*) as 'Number of Courses' FROM mdl_course"
query_lessons = "SELECT COUNT(h.id) AS num_of_lessons FROM mdl_course c JOIN mdl_hvp h ON h.course = c.id GROUP BY c.fullname;"
    #"SELECT C.fullname as 'Course Name', COUNT(A.id) as 'Number of Lessons' FROM mdl_course C JOIN mdl_h5pactivity A ON C.id = A.course GROUP BY C.fullname"
query_enrolled = "SELECT COUNT(*) AS 'Number of Students Enrolled' FROM mdl_user_enrolments ue INNER JOIN mdl_enrol e ON ue.enrolid = e.id INNER JOIN mdl_course c ON e.courseid = c.id GROUP BY c.fullname"
query_badges = "SELECT COUNT(*) AS 'Number of Badges Obtained' FROM mdl_badge_issued bi INNER JOIN mdl_badge b ON bi.badgeid = b.id INNER JOIN mdl_course c ON b.courseid = c.id GROUP BY c.fullname"

# Execute queries and store results in a dataframe
df = pd.DataFrame()
df = df.append(pd.read_sql_query(query_users, engine), ignore_index=True)
df = df.append(pd.read_sql_query(query_courses, engine), ignore_index=True)
df = df.append(pd.read_sql_query(query_lessons, engine), ignore_index=True)
df = df.append(pd.read_sql_query(query_enrolled, engine), ignore_index=True)
df = df.append(pd.read_sql_query(query_badges, engine), ignore_index=True)

print(df)

# Create a dashboard using Panel
# pn.extension()
# dashboard = pn.Column(
#     pn.Row(
#         pn.pane.Markdown("# Moodle Dashboard"),
#         width=12
#     ),
#     pn.Row(
#         pn.Card(
#             pn.indicators.Number(value=all_users, default_color='white',
#                             name='Number of All Users', format='{value}'),
#                   background='#17A589',
#                   hide_header=True,
#                   width=160
#               ),
#         pn.Card(
#             pn.indicators.Number(value=courses, default_color='white',
#                             name='Number of Courses', format='{value}'),
#                   background='#17A589',
#                   hide_header=True,
#                   width=160
#               ),
#         width=12
#     ),
#     pn.Row(
#         pn.pane.DataFrame(df_courses, width=800, escape=False, index=False),
#         width=12
#     ),
#     pn.Row(
#         pn.pane.DataFrame(df_enrollments, width=800, escape=False, index=False),
#         width=12
#     ),
#     pn.Row(
#         pn.pane.DataFrame(df_badges, width=800, escape=False, index=False),
#         width=12
#     ),
# )
#
# dashboard.servable()
