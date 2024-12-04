import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from geodatasets import get_path
from shapely import wkt

sns.set_theme(style="ticks", palette="pastel")
df_colors = pd.read_csv('MTA_Colors.csv')
df_riders = pd.read_csv('MTA_DailyRidershipData.csv')
df_stations = pd.read_csv('MTA_SubwayStations.csv')

# *** LINE PLOT

# Convert Date column to time-series format
df_riders['Date'] = pd.to_datetime(df_riders['Date'])

# Filter the dataframe for dates from 2020 to 2021
# df_riders_filtered = df_riders[(df_riders['Date'] >= '2020-01-01') & (df_riders['Date'] <= '2021-12-31')]

plt.figure(figsize=(14, 7))
sns.lineplot(data=df_riders, x='Date', y='Subways: Total Estimated Ridership', label='Daily Total Estimated Riders')
plt.title('Subway Ridership Over Time (2020-2021)')
plt.xlabel('Date')
plt.ylabel('Subway Ridership')
plt.legend()
plt.xticks(rotation=45)
plt.savefig('subway_ridership.png', bbox_inches='tight')
plt.close()

# SCATTER PLOT

# Filter stations to include Manhattan only
df_stations_filtered = df_stations[df_stations['Borough'] == 'M'].reset_index(drop=True)

sns.scatterplot(data=df_stations_filtered, x='GTFS Longitude', y='GTFS Latitude')
'''
# Add labels to the scatter plot
for i in range(df_stations_filtered.shape[0]):
    plt.text(x=df_stations_filtered['GTFS Longitude'][i], y=df_stations_filtered['GTFS Latitude'][i], s=df_stations_filtered['Stop Name'][i], 
             fontdict=dict(size=6), bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
'''
plt.title('Manhattan Subway Stations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig('stations_scatter_plot.png', bbox_inches='tight')
plt.close()

# *** MAP PLOT ***

# Load the nybb dataset
nybb = gpd.read_file(get_path('nybb'))
manhattan = nybb[nybb.BoroName == 'Manhattan']

# Convert the df_stations_filtered to a GeoDataFrame
gdf_stations = gpd.GeoDataFrame(df_stations_filtered, geometry=gpd.points_from_xy(df_stations_filtered['GTFS Longitude'], df_stations_filtered['GTFS Latitude']))

# Ensure both GeoDataFrames use the same CRS (coordinate reference system)
gdf_stations.set_crs(epsg=4326, inplace=True)  # Assuming the station data is in WGS84 (latitude/longitude)
manhattan = manhattan.to_crs(epsg=4326)  # Convert Manhattan map to WGS84

# Plot the map and the scatter plot
fig, ax = plt.subplots(figsize=(10, 8))
manhattan.plot(ax=ax, color='lightgrey')
gdf_stations.plot(ax=ax, color='#0039A5', markersize=5)

'''
# Add labels to the scatter plot
for x, y, label in zip(gdf_stations.geometry.x, gdf_stations.geometry.y, gdf_stations['Stop Name']):
    plt.text(x, y, label, fontsize=8, color='red', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
'''

plt.title('Manhattan Subway Map')
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_facecolor('lightblue')
plt.savefig('subway_map.png', bbox_inches='tight')
plt.close()

# *** CATEGORICAL PLOT ***

# Filter only New York City Subway lines
df_colors = df_colors[df_colors['Operator'] == 'New York City Subway'].reset_index()
# Split the Service column by commas 
df_colors['Service'] = df_colors['Service'].str.split(',')
# Explode the DataFrame so that each row contains only one subway line
df_colors_exploded = df_colors.explode('Service')
# Group by color and count the number of subway lines
color_counts = df_colors_exploded.groupby('Hex color')['Service'].count().reset_index()
color_counts.columns = ['Color', 'Count']
# Sort the color_counts DataFrame by the Count column
color_counts = color_counts.sort_values(by='Count', ascending=False)
print(color_counts)

# Create a bar plot
plt.figure(figsize=(12, 6))
sns.barplot(data=color_counts, x='Color', y='Count', palette=color_counts['Color'].tolist())
plt.title('Number of Subway Lines per Color')
plt.xlabel('Hex Color Code')
plt.ylabel('Number of Subway Lines')
plt.yticks([1, 2, 3, 4])

# Create a dictionary to map each color to the corresponding subway lines
color_to_lines = df_colors_exploded.groupby('Hex color')['Service'].apply(lambda x: ', '.join(x.unique())).to_dict()
# Create custom legend
handles = [plt.Line2D([0], [0], marker='o', color=color, linestyle='', markersize=10) for color in color_counts['Color']]
labels = [f"{color_to_lines[color]}" for color in color_counts['Color']]
plt.legend(handles, labels, loc='best')

plt.savefig('colors_catplot.png', bbox_inches='tight')
plt.close()

# *** STACKED BAR PLOT ***
# Filter the dataframe for dates from 2020 to 2021
df_riders_filtered = df_riders[(df_riders['Date'] >= '2020-01-01') & (df_riders['Date'] <= '2020-12-31')]

# Set the Date column as the index
df_riders_filtered.set_index('Date', inplace=True)
df_riders_filtered.rename(columns={
    'Subways: Total Estimated Ridership': 'Subways',
    'Buses: Total Estimated Ridership': 'Buses',
    'LIRR: Total Estimated Ridership': 'LIRR',
    'Metro-North: Total Estimated Ridership': 'Metro-North',
    'Access-A-Ride: Total Scheduled Trips': 'Access-A-Ride',
    'Bridges and Tunnels: Total Traffic': 'Bridges & Tunnels',
    'Staten Island Railway: Total Estimated Ridership': 'Staten Island Railway'
}, inplace=True)

# Select the columns for the stacked bar plot
columns_to_plot = [
    'Subways',
    'Buses',
    'LIRR',
    'Metro-North',
    'Bridges & Tunnels'
]

# Plot the stacked bar plot
df_riders_filtered[columns_to_plot].resample('ME').sum().plot(kind='bar', stacked=True, figsize=(14, 7))

plt.title('Monthly MTA Ridership by Transportation Mode (2020)')
plt.xlabel('Month')
plt.ylabel('Total Ridership')
plt.legend(title='Transportation Mode', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('stacked_bar_plot.png', bbox_inches='tight')
plt.close()

# Calculate the sum of each row
row_sums = df_riders_filtered[columns_to_plot].resample('ME').sum().sum(axis=1)

# Normalize the data to get percentages
df_normalized = df_riders_filtered[columns_to_plot].resample('ME').sum().div(row_sums, axis=0)

# Plot the 100% stacked bar plot
df_normalized.plot(kind='bar', stacked=True, figsize=(14, 7))

plt.title('Monthly MTA Ridership by Transportation Mode (2020) - 100% Stacked')
plt.xlabel('Month')
plt.ylabel('Percentage of Total Ridership')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.savefig('stacked_bar_plot_100.png', bbox_inches='tight')
