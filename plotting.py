import cartopy
import pandas as pd
from solar_utils import daynight_grid, sun_pos
import matplotlib.pyplot as plt

def plot_daynight(ax, dt, transform):
    # plot sun position
    lat, lng = sun_pos(dt=dt)
    sun = plt.Circle((lng, lat), 3, facecolor='yellow', edgecolor='black', alpha=0.5, transform=transform, zorder=99, label='Sun')
    ax.add_patch(sun)

    # draw daynight
    lons,lats,daynight = daynight_grid(date=dt, delta=0.25, lonmin=-180, lonmax=180)
    ax.contourf(lons, lats, daynight, 1, colors=['k'], alpha=0.5, transform=transform)


def plot_map_features(ax):
    ax.set_global()

    # plot map with features
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)


def plot_ground_path(ax, df, transform, daynight=True, cmap='Oranges'):    
    dt = df.index[-1]

    # add basemap, coastlines and borders
    plot_map_features(ax)
    
    # color generator
    NUM_COLORS = len(df['orbit'].unique())
    cm = plt.cm.get_cmap(cmap)
    cgen = (cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS))
    
    # plot orbits
    for orbit in df['orbit'].unique():
        mask = df['orbit'] == orbit
        ax.plot(df[mask]['lon'], df[mask]['lat'], color=next(cgen), label='Orbit {:}'.format(orbit), transform=transform)
    
    # plot satellite starting position
    start_pos = plt.Circle((df.iloc[0]['lon'], df.iloc[0]['lat']), 2, facecolor='green', edgecolor='black', alpha=0.5, transform=transform, zorder=99, label='Start')
    end_pos = plt.Circle((df.iloc[-1]['lon'], df.iloc[-1]['lat']), 2, facecolor='red', edgecolor='black', alpha=0.5, transform=transform, zorder=99, label='End')
    ax.add_patch(start_pos)
    ax.add_patch(end_pos) 
    
    if daynight:
        plot_daynight(ax, dt, cartopy.crs.PlateCarree())

    