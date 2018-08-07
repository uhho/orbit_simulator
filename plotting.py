import cartopy
import pandas as pd
from solar_utils import daynight_grid, sun_pos

def plot_ground_path(ax, df, title, transform, daynight=True, legend=True):    
    dt = df.index[-1]
    ax.set_global()

    # plot map with features
    ax.stock_img()
    ax.coastlines()
    ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)

    # plot orbits
    for orbit in df['orbit'].unique():
        mask = df['orbit'] == orbit
        ax.plot(df[mask]['lon'], df[mask]['lat'], label='Orbit {:}'.format(orbit), transform=transform)
    
    # plot satellite starting position
    ax.plot(df.iloc[0]['lon'], df.iloc[0]['lat'], color='green', markersize=10, markeredgecolor='black', marker='o', alpha=0.5, transform=transform)
    ax.plot(df.iloc[-1]['lon'], df.iloc[-1]['lat'], color='red', markersize=10, markeredgecolor='black', marker='o', alpha=0.5, transform=transform)

    # plot sun position
    if daynight:
        lat, lng = sun_pos(dt=dt)
        ax.plot([lng], [lat], color='black', marker='$☉$', markersize=20, linewidth=0, alpha=0.5, label='Sun', transform=transform)

        # draw daynight
        lons,lats,daynight = daynight_grid(date=dt, delta=0.25, lonmin=-180, lonmax=180)
        ax.contourf(lons, lats, daynight, 1, colors=['k'], alpha=0.5, transform=transform)

    ax.set_title(title)
    if legend:
        ax.legend(loc='upper left')