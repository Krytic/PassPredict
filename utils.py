import functools
import twitter
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import WorksheetNotFound
from pytz import timezone

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

class ValidationError(Exception):
    pass


def memoize(func):
    cache = func.cache = {}

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


@memoize
def load_config():
    cfg = dict()
    cfg['twitter'] = dict()

    with open('config.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == "#" or line.strip() == "":
                continue
            bits = line.split('=')

            value = bits[1].strip()

            if value in ['True', 'False']:
                value = bool(value)

            if bits[0][:3] == "tw:":
                cfg['twitter'][bits[0][3:]] = value
            else:
                cfg[bits[0]] = value

    return cfg


def fetch_tracked_satellites():
    cfg = load_config()

    if cfg['run_mode'] == 'normal':
        with open('tracking.txt', 'r') as f:
            satellites = f.readlines()
    elif cfg['run_mode'] == 'dynamic':
        ws = worksheet()
        satellites = ws.col_values(1)[1:]  # Assume that the worksheet has header row

    return satellites


@memoize
def twitter_api():
    cfg = load_config()
    api = twitter.Api(**cfg['twitter'])
    if not api.VerifyCredentials():
        raise ValidationError('Incorrect twitter credentials!')

    return api


@memoize
def worksheet():
    cfg = load_config()

    # API recently changed, not sure which scope is required
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(
            'client_secret.json',
            scope
            )
    client = gspread.authorize(creds)

    try:
        ws = client.open_by_key(cfg['sheet_id']).worksheet(cfg['sheet_name'])
    except WorksheetNotFound:
        raise ValidationError("Incorrect sheet details. \
                              Confirm that sheet_name and sheet_id are \
                              correctly set in config.txt")

    return ws


def construct_image(sat, path, trange, gs, sat_name, trange_plot):
    cfg = load_config()
    ax = plt.subplot(121)
    
    az, el = compute_azel(sat, gs, trange)
    
    ax2 = ax.twinx()
    plt.ylim(0, 90)
    ax.plot(trange_plot, el, 'b-')
    ax2.plot(trange_plot, az, 'r-')
    ax.set_ylim(0, 90)
    ax2.set_ylim(0, 360)
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_ticks([])
    
    plt.xlabel("Time")
    ax.set_ylabel("Elevation")
    ax2.set_ylabel("Azimuth")
    
    plt.subplot(122)
    map = Basemap(projection="ortho", lat_0=cfg['gs_lat'], lon_0=cfg['gs_long'], resolution='l')
    
    # draw lat/lon grid lines every 30 degrees.
    map.drawmeridians(np.arange(0,360,30))
    map.drawparallels(np.arange(-90,90,30))
    map.drawmapboundary(fill_color="navy")
    map.drawcoastlines()
    map.fillcontinents(color='darkgreen', lake_color='navy')
    lon = path.longitude.degrees
    lat = path.latitude.degrees
    
    map.plot(lon,lat,zorder=100,latlon=True,marker='x',color='y',markersize=2)

    plt.suptitle("{} Pass Data".format(sat_name))
    
    return plt

def compute_azel(satellite, ground_station, trange):
    azimuth, elevation = [], []
    for tp in trange:
        diff = satellite - ground_station
        diff = diff.at(tp)
        altaz = diff.altaz()
        elevation.append(altaz[0].degrees)
        azimuth.append(altaz[1].degrees)
    
    return azimuth, elevation

def compute_maximum_elevation(satellite, ground_station, trange):
    cfg = load_config()

    local_time = timezone(cfg['gs_tz'])
    maximum_elevation = (0, '')
    for tp in trange:
        diff = satellite - ground_station
        diff = diff.at(tp)
        elv = float(diff.altaz()[0].degrees)
        if elv > maximum_elevation[0]:
            maximum_elevation = (elv, tp.astimezone(local_time).strftime("%I:%M:%S %p"))

    return maximum_elevation
