#Install this package before running - pip install -U kaleido
from shiny import App, ui, render
import pandas as pd
import plotly.express as px
import os

if not os.path.exists("plots"):
    os.mkdir("plots")

df = pd.read_csv("quakes-cleaned.csv")

df['time'] = pd.to_datetime(df['time'], errors='coerce', format='mixed')
df = df[df['mag'] > 0]  


high_risk_zones = df.groupby(['latitude', 'longitude']).size().reset_index(name='count')
high_risk_zones = high_risk_zones.sort_values(by='count', ascending=False).head(5)

most_affected_places = df['place'].value_counts().reset_index().head(10)
most_affected_places.columns = ['place', 'count']

df['hour'] = df['time'].dt.hour
earthquake_frequency_by_hour = df['hour'].value_counts().sort_index().reset_index()
earthquake_frequency_by_hour.columns = ['hour', 'frequency']


avg_magnitude = df['mag'].mean()


def save_plotly_fig(fig, filename):
    """Save Plotly figure as a PNG image."""
    fig.write_image(f"plots/{filename}")


save_plotly_fig(
    px.scatter_geo(
        high_risk_zones,
        lat='latitude',
        lon='longitude',
        size='count',
        color='count',
        title="Top 5 High-Risk Zones (Geographic Map)",
        labels={"count": "Earthquake Count"},
        projection="natural earth"
    ),
    "high_risk_map.png"
)

most_seismic_area = high_risk_zones.iloc[0]
save_plotly_fig(
    px.scatter_geo(
        df,
        lat='latitude',
        lon='longitude',
        size='mag',
        title=f"Most Seismic Activity: Lat {most_seismic_area['latitude']}, Lon {most_seismic_area['longitude']}",
        labels={"latitude": "Latitude", "longitude": "Longitude", "mag": "Magnitude"}
    ).add_scattergeo(
        lat=[most_seismic_area['latitude']],
        lon=[most_seismic_area['longitude']],
        marker=dict(size=15, color='red'),
        name="Most Active Zone"
    ),
    "most_seismic_activity.png"
)

save_plotly_fig(
    px.bar(
        most_affected_places,
        x='place',
        y='count',
        text='count',
        title="Top 10 Most Affected Places",
        labels={"place": "Place", "count": "Earthquake Count"}
    ).update_xaxes(tickangle=45),
    "most_affected_places.png"
)

save_plotly_fig(
    px.line(
        earthquake_frequency_by_hour,
        x='hour',
        y='frequency',
        title="Earthquake Frequency by Hour",
        labels={"hour": "Hour of Day (0-23)", "frequency": "Earthquake Count"}
    ),
    "hourly_frequency_plot.png"
)

save_plotly_fig(
    px.histogram(
        df,
        x='mag',
        nbins=50,
        title=f"Distribution of Earthquake Magnitudes (Average: {avg_magnitude:.2f})",
        labels={"mag": "Magnitude", "count": "Frequency"}
    ).add_vline(
        x=avg_magnitude,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg Magnitude: {avg_magnitude:.2f}"
    ),
    "magnitude_distribution_plot.png"
)


app_ui = ui.page_fluid(
    ui.h2("Earthquake Analysis Dashboard"),
    ui.navset_tab(
        ui.nav_panel(
            "Top 5 High-Risk Zones",
            ui.output_image("high_risk_map")
        ),
        ui.nav_panel(
            "Most Seismic Activity",
            ui.output_image("most_seismic_activity")
        ),
        ui.nav_panel(
            "Most Affected Places",
            ui.output_image("most_affected_places")
        ),
        ui.nav_panel(
            "Earthquake Frequency by Hour",
            ui.output_image("hourly_frequency_plot")
        ),
        ui.nav_panel(
            "Magnitude Distribution",
            ui.output_image("magnitude_distribution_plot")
        )
    )
)


def server(input, output, session):
    @output
    @render.image
    def high_risk_map():
        return {"src": "plots/high_risk_map.png", "alt": "High-Risk Zones Map"}

    @output
    @render.image
    def most_seismic_activity():
        return {"src": "plots/most_seismic_activity.png", "alt": "Most Seismic Activity Map"}

    @output
    @render.image
    def most_affected_places():
        return {"src": "plots/most_affected_places.png", "alt": "Most Affected Places Bar Chart"}

    @output
    @render.image
    def hourly_frequency_plot():
        return {"src": "plots/hourly_frequency_plot.png", "alt": "Earthquake Frequency by Hour"}

    @output
    @render.image
    def magnitude_distribution_plot():
        return {"src": "plots/magnitude_distribution_plot.png", "alt": "Magnitude Distribution"}

app = App(app_ui, server)