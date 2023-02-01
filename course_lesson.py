import panel as pn
from sqlalchemy import create_engine
import pandas as pd
import hvplot.pandas

# Connect to database and retrieve data using SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/moodle')
query = "SELECT COUNT(h.id) AS num_of_lessons, c.fullname FROM mdl_course c JOIN mdl_hvp h ON h.course = c.id GROUP BY c.fullname;"
df = pd.read_sql_query(query, engine)

# Create a dropdown widget with the list of courses
dropdown = pn.widgets.Select(name='Courses', options=['Select'] + df['fullname'].tolist())

# Define a function to update the plot based on the selected course
# def update_plot(event):
#     selected_course = event.new
#     filtered_df = df[df['fullname'] == selected_course]
#     plot.y = filtered_df['num_of_lessons'].tolist()
#     plot.title = f"Number of Lessons for {selected_course}:
def update_plot(event):
    selected_course = event.new
    filtered_df = df[df['fullname'] == selected_course]
    plot.object = filtered_df.hvplot.bar(x='fullname', y='num_of_lessons', title=f"Number of Lessons for {selected_course}")


# Link the function to the dropdown widget
dropdown.param.watch(update_plot, 'value')

# Create a plot with all the values at the initial load
plot = pn.pane.HoloViews(df.hvplot.bar(x='fullname', y='num_of_lessons', title='Number of Lessons for All Courses'))

# plot = pn.pane.Plotly(y=df['num_of_lessons'].tolist(), x=df['fullname'].tolist(), title='Number of Lessons for All Courses')

# # Combine the dropdown widget and the plot in a layout
# layout = pn.Row(dropdown, plot)
#
# # Display the layout using panel serve
# pn.serve(layout)

# Use a fast list template to structure the layout
template = pn.template.FastListTemplate(
    site='Lesson',
    # sidebar='',
    main=[dropdown, plot]
)

# Serve the template
template.servable()
