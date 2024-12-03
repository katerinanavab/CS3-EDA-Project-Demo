import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="ticks", palette="pastel")
df_colors = pd.read_csv('MTA_Colors.csv')
df_riders = pd.read_csv('MTA_KeyPerformanceIndicators.csv')
df_stations = pd.read_csv('MTA_SubwayStations.csv')


