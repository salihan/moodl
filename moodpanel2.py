import pandas as pd
from sqlalchemy import create_engine
import panel as pn
import hvplot.pandas

# Create a database connection
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

query1 = """SELECT l.courseid, c.fullname as course_name, 
    l.contextinstanceid as activity_id, mdl_modules.name as activity_name, 
    SUM(UNIX_TIMESTAMP() - l.timecreated) as duration, 
    COUNT(DISTINCT l.userid) as student_count 
    FROM mdl_logstore_standard_log l 
    JOIN mdl_course c ON l.courseid = c.id JOIN mdl_course_modules cm ON l.contextinstanceid = cm.id 
    JOIN mdl_modules ON cm.module = mdl_modules.id 
    WHERE l.action = 'viewed' GROUP BY l.courseid, l.contextinstanceid ORDER BY duration DESC"""

# Execute the query
df = pd.read_sql(query1, engine)

# Create a scatter plot of duration vs student count
scatter = df.hvplot.scatter(x='student_count', y='duration', title='Duration vs Student Count')

# Create a Column layout
col = pn.Column(scatter)

# Create a Row layout with the columns
row = pn.Row(col)

# Create a Panel
panel = pn.panel(row, template=pn.template.FastListTemplate)

# Show the panel
panel.show()
