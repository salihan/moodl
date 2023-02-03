import pandas as pd
from sqlalchemy import create_engine
import panel as pn
pn.extension()
import hvplot.pandas

# Create a database connection save it in csv
engine = create_engine('mysql+pymysql://root:@localhost/moodle')
df = pd.read_sql_query("SELECT * FROM mdl_task_log", engine)
df.to_excel('moodle_task_logs.xlsx', index=False)
# df.to_csv('moodle_task_logs.csv', index=False)

# Load data into a pandas DataFrame
df = pd.read_excel('moodle_task_logs.xlsx')

# Create a timestamp column from the timestart column
df['timestamp'] = pd.to_datetime(df['timestart'], unit='s')

# Create a duration column from the timeend column
df['duration'] = (df['timeend'] - df['timestart']) / 60

# Define the pipeline
timestamp_slider = pn.widgets.DateRangeSlider(name='Select Time Range', value=(df['timestamp'].min(), df['timestamp'].max()), start=df['timestamp'].min(), end=df['timestamp'].max(), step=1)
# timestamp_slider = pn.widgets.RangeSlider(start=df['timestamp'].min(), end=df['timestamp'].max(), value=(df['timestamp'].min(), df['timestamp'].max()), step=1, name='Timestamp Slider')
idf = df.interactive()
tasklog_plot_pipeline = (idf[(idf.timestamp >= timestamp_slider.value[0]) & (idf.timestamp <= timestamp_slider.value[1])])

tasklog_plot = tasklog_plot_pipeline.hvplot(kind='line', x='timestamp', y='duration', title='Task Duration Over Time')

#------------------
# Define the callback function to update the plot when the range changes
def update_plot(event):
    tasklog_plot_pipeline = ( idf[ (idf.timestamp >= event.new[0]) & (idf.timestamp <= event.new[1]) ] )
    tasklog_plot.data = tasklog_plot_pipeline


# Attach the callback function to the timestamp_slider
timestamp_slider.param.watch(update_plot, 'value')

#------------------

#Layout using Template
template = pn.template.FastListTemplate(
    title='Task Duration Dashboard',
    sidebar=[pn.pane.Markdown("# Course engagement analysis"),
             pn.pane.Markdown("#### Analyze student engagement in the course by analyzing their activity in the course, such as number of logins, forum posts, and quiz attempts."),
             # pn.pane.PNG('climate_day.png', sizing_mode='scale_both'),
             pn.pane.Markdown("## Settings"),
             timestamp_slider],
    main=[
          pn.Row(#pn.Column(co2_vs_gdp_scatterplot.panel(width=600), margin=(0,25)),
                 pn.Column(tasklog_plot.panel(width=600), margin=(0,25)))
    ],
    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)
# template.show()
template.servable();