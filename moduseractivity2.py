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
bar = df.hvplot.bar(x='course_id', y='duration', groupby='firstname', title='Time spent by user in course')

# Create a table of last access time
table = pn.widgets.DataFrame(df[['firstname','lastname','course_name','last_access']], title="")

# Create a histogram of access count
hist = df['access_count'].hvplot.hist(title='Access count per user')

# Create a Column layout with the bar chart, table, and histogram
col = pn.Column(bar, table, hist)

# Create a dropdown menu for course selection
courses = df['course_name'].unique()
courses = ['All'] + list(courses)
course_select = pn.widgets.Select(name='Course', options=courses, value='All')

# Create a callback function that updates the plot based on the selected course
def update_plot(event):
    if event.new == 'All':
        bar.update(df)
    else:
        bar.update(df[df['course_name'] == event.new])

# Link the dropdown menu to the callback function
course_select.param.watch(update_plot, 'value')

# Apply the template to the panel
template = pn.template.FastListTemplate(site="Cassmile", title="User Activity Analysis", main=col, sidebar=course_select)

# Make the template and the dashboard accessible through the 'panel serve' command
template.servable()
