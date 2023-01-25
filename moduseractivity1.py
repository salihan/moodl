import pandas as pd
from sqlalchemy import create_engine
import panel as pn
import hvplot.pandas

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

# Execute the query
query = """
SELECT u.firstname, u.lastname, c.id as course_id, c.fullname as course_name, 
MAX(ul.timeaccess) as last_access,
SUM(UNIX_TIMESTAMP() - ul.timeaccess) as duration, 
COUNT(DISTINCT ul.userid) as access_count
FROM mdl_user_lastaccess ul
JOIN mdl_user u on u.id = ul.userid
JOIN mdl_course c on c.id = ul.courseid
GROUP BY ul.userid, ul.courseid
ORDER BY duration DESC
"""
df = pd.read_sql(query, engine)

# Create a bar chart of user's course duration
bar = df.hvplot.bar(x='course_id', y='duration', title='Time spent by user in course')
# barchart = df.hvplot.bar(x='course_id', y='student_count', title = 'Number of students per course')

# Create a table of last access time
table = pn.widgets.DataFrame(df[['firstname','lastname','course_name','last_access']])

# Create a histogram of access count
# hist = df['access_count'].hvplot.hist(title='Access count per user', bins=20)
hist = df.hvplot.hist(
                    y=["access_count"],
                    width=500, height=400,
                    ylim=(0,50),
                    bins=20,
                    alpha=0.9,
                    color="orangered",
                    ylabel="Frequency",
                    title="Access count per user")


template = pn.template.FastListTemplate(
    site="Cassmile", title="User Activity Analysis",
    main=[pn.Row(pn.Column(table)),
          pn.Row(pn.pane.HoloViews(bar), sizing_mode = 'stretch_width'),
          pn.Row(pn.pane.HoloViews(hist), sizing_mode = 'stretch_width')]
)
template.servable();