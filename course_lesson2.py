import pandas as pd
from sqlalchemy import create_engine
import panel as pn
pn.extension()
import hvplot.pandas

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

# Load the data into a pandas DataFrame
df = pd.read_sql("SELECT * FROM mdl_user", engine)
# 1) Calculate the number of users
num_users = len(df)

# execute the query for enrolled students
query_enrolled = "SELECT COUNT(DISTINCT ue.userid) AS 'Enrolled Students' FROM mdl_user_enrolments ue"
result_enrolled = pd.read_sql(query_enrolled, engine)  # .to_string(index=False)
num_enrolled = result_enrolled['Enrolled Students'].iloc[0]

# execute the query for active students
query_active = """SELECT COUNT(DISTINCT u.id) as 'Active Students' FROM mdl_user u 
JOIN mdl_user_enrolments ue ON ue.userid = u.id
JOIN mdl_enrol e ON e.id = ue.enrolid
WHERE u.deleted = 0 AND u.suspended = 0 AND e.status = 0"""
result_active = pd.read_sql(query_active, engine)  # .to_string(index=False)
num_active = result_active['Active Students'].iloc[0]

# 2) Load the course data into a pandas DataFrame
df_courses = pd.read_sql("SELECT * FROM mdl_course", engine)
# Calculate the number of courses
num_courses = len(df_courses)

# x) Load the enrollment data into a pandas DataFrame
df_courses_enrollments = pd.read_sql_query(
    '''
    SELECT c.fullname, c.shortname, COUNT(ue.userid) AS num_enrollments
    FROM mdl_course c
    JOIN mdl_enrol e ON c.id = e.courseid
    JOIN mdl_user_enrolments ue ON e.id = ue.enrolid
    GROUP BY c.fullname;
    ''', engine)

# Plot the number of students enrolled in each course
enrollment_plot = df_courses_enrollments.hvplot.bar(x='shortname', y='num_enrollments', height=400, xaxis=None,
                                                    color='shortname', cmap='Category20',
                                                    title="Number of Students Enrolled in Each Course")

# 3) number of lessons (h5p) in each course
df_courses_h5p = pd.read_sql_query('''
    SELECT c.fullname AS course_name, c.shortname, COUNT(l.id) AS num_h5p
    FROM mdl_course c
    JOIN mdl_hvp l ON l.course = c.id
    GROUP BY c.fullname;
''', engine)
h5p_plot = df_courses_h5p.hvplot.bar(x='course_name', y='num_h5p', rot=90, height=400, xaxis=None, color='shortname',
                                     cmap='Category20', title="Number of Lessons (h5p) in Each Course")

# 4) Create a SQL query to get the number of students obtained badges in each course
badges_query = "SELECT c.fullname AS course_name, c.shortname, COUNT(*) AS 'num_badges' FROM mdl_badge_issued bi inner JOIN mdl_badge b ON bi.badgeid = b.id INNER JOIN mdl_course c ON b.courseid = c.id GROUP BY c.id"
# Execute the query and store the result in a Pandas DataFrame
badges_df = pd.read_sql(badges_query, engine)
# Create a bar plot to show the number of students obtained badges in each course
badges_plot = badges_df.hvplot.bar(x='course_name', y='num_badges', height=400, width=700, color='shortname',
                                   cmap='Category20', xaxis=None,
                                   title="Number of Students Obtained Badges in Each Course")

# 5) Query to get the number of students obtained badges in each course
query = '''
SELECT u.firstname, u.lastname, c.fullname as course_name, count(bi.userid) as num_badges
FROM mdl_user u
JOIN mdl_badge_issued bi ON u.id = bi.userid
JOIN mdl_badge b ON bi.badgeid = b.id
JOIN mdl_course c ON b.courseid = c.id
GROUP BY c.id, bi.userid
'''
# Fetch the data from the database
badges_df = pd.read_sql(query, engine)
widget_badges = pn.widgets.DataFrame(badges_df)

# get all course for select in setting
df_course_select = pd.read_sql("SELECT * FROM mdl_course", engine)
courses = df_course_select['shortname'].unique()
courses = ['ALL'] + list(courses)
course_select = pn.widgets.Select(name='Course', options=courses, value="*")

template = pn.template.FastListTemplate(
    site="Cassmile", title="Student-Courses Analysis",
    sidebar=[pn.pane.Markdown("## Settings"), course_select],
    main=[pn.Row(
        pn.Card(pn.indicators.Number(value=num_users, default_color='white', name='Number of Users', title_size='12pt',
                                     format='{value}', font_size='45pt'),
                background='#17A589',
                hide_header=True,
                width=160

                ),
        pn.Card(
            pn.indicators.Number(value=num_courses, default_color='white', name='Number of Courses', title_size='12pt',
                                 format='{value}', font_size='45pt'),
            background='#884EA0',
            hide_header=True,
            width=160

            ),
        pn.Card(
            pn.indicators.Number(value=num_enrolled, default_color='white', name='Enrolled Students', title_size='12pt',
                                 format='{value}', font_size='45pt'),
            background='#F5B041',
            hide_header=True,
            width=160

            ),
        pn.Card(pn.indicators.Number(value=num_active, default_color='white', name='Active Students', title_size='12pt',
                                     format='{value}', font_size='45pt'),
                background='#3C8AE7',
                hide_header=True,
                width=160

                )
        # pn.Card(
        #     pn.pane.Markdown(f"<h1 style='font-size:24px; color:white' align='center'>Active Students</h1><h2 style='font-size:40px; color:white' align='center'>{num_active}</h2>"),
        #     background='#3C8AE7', width=160, height=200
        # )
    ),
    # pn.Row(df_courses_enrollments.hvplot.bar(x='fullname', y='id_enrollments', height=400))
    pn.Row(enrollment_plot),
    pn.Row(h5p_plot),
    pn.Row(badges_plot),
    pn.Row(widget_badges)]
)
template.servable();


# Create a dashboard using Panel
# dashboard = pn.Column(
#     pn.Row(
#         pn.Card(pn.indicators.Number(value=num_users, default_color='white', name='Number of Users', title_size='12pt',
#                                      format='{value}', font_size='45pt'),
#                 background='#17A589',
#                 hide_header=True,
#                 width=160
#
#                 ),
#         pn.Card(
#             pn.indicators.Number(value=num_courses, default_color='white', name='Number of Courses', title_size='12pt',
#                                  format='{value}', font_size='45pt'),
#             background='#884EA0',
#             hide_header=True,
#             width=160
#
#             ),
#         pn.Card(
#             pn.indicators.Number(value=num_enrolled, default_color='white', name='Enrolled Students', title_size='12pt',
#                                  format='{value}', font_size='45pt'),
#             background='#F5B041',
#             hide_header=True,
#             width=160
#
#             ),
#         pn.Card(pn.indicators.Number(value=num_active, default_color='white', name='Active Students', title_size='12pt',
#                                      format='{value}', font_size='45pt'),
#                 background='#3C8AE7',
#                 hide_header=True,
#                 width=160
#
#                 )
#         # pn.Card(
#         #     pn.pane.Markdown(f"<h1 style='font-size:24px; color:white' align='center'>Active Students</h1><h2 style='font-size:40px; color:white' align='center'>{num_active}</h2>"),
#         #     background='#3C8AE7', width=160, height=200
#         # )
#     ),
#     # pn.Row(df_courses_enrollments.hvplot.bar(x='fullname', y='id_enrollments', height=400))
#     pn.Row(enrollment_plot),
#     pn.Row(h5p_plot),
#     pn.Row(badges_plot),
#     pn.Row(widget_badges)
# )
#
# # Serve the dashboard
# dashboard.servable()