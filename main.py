import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="ticks", palette="pastel")
df_colors = pd.read_csv('MTA_Colors.csv')
df_riders = pd.read_csv('MTA_DailyRidershipData.csv')
df_stations = pd.read_csv('MTA_SubwayStations.csv')

# Convert Date column to time-series format
df_riders['Date'] = pd.to_datetime(df_riders['Date'])

# Filter the dataframe for dates from 2020 to 2021
# df_riders_filtered = df_riders[(df_riders['Date'] >= '2020-01-01') & (df_riders['Date'] <= '2021-12-31')]

# LINE PLOT
plt.figure(figsize=(14, 7))
sns.lineplot(data=df_riders, x='Date', y='Subways: Total Estimated Ridership', label='Daily Total Estimated Riders')
plt.title('Subway Ridership Over Time (2020-2021)')
plt.xlabel('Date')
plt.ylabel('Subway Ridership')
plt.legend()
plt.xticks(rotation=45)
plt.savefig('subway_ridership.png', bbox_inches='tight')

