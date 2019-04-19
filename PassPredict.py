from mpl_toolkits.basemap import Basemap
import twitter
from skyfield.api import Topos, load, utc
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sched, time
from pytz import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import utils

mode = "normal"
silent = False

if len(sys.argv) > 1:
    mode = sys.argv[1] if sys.argv[1] == "dynamic" else "normal"
    silent = True if sys.argv[2] == "silent" else False

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive'] # API recently changed, not sure which scope is required
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

cfg = utils.load_config()

api = twitter.Api(**cfg['twitter'])
ws = client.open_by_key(cfg['sheet_id']).worksheet(cfg['sheet_name'])

local_time = timezone(cfg['gs_tz'])

if not api.VerifyCredentials():
    raise ValueError('Incorrect twitter credentials!')

if mode == 'normal':
    with open('tracking.txt', 'r') as f:
        sats = f.readlines()
elif mode == 'dynamic':
    sats = ws.col_values(1)[1:] # header

tweeted = []

min_range = 15

def check():
    for i in range(len(sats)):
        now = datetime.datetime.utcnow()
        mtime = now + datetime.timedelta(minutes=min_range)
        
        sats[i] = sats[i].strip().upper()
        
        sat = sats[i]
        
        ts = load.timescale()
        t = ts.utc(mtime.replace(tzinfo=utc))
        
        secs = np.arange(1, 60*(min_range+15))
        
        trange = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second+secs)
        
        
        stations_url = 'http://celestrak.com/NORAD/elements/active.txt'
        satellites = load.tle(stations_url, reload=reload)
        
        if reload:
            reload = False
        
        if sat not in satellites:
            continue
        
        satellite = satellites[sat]
        
        latitude = np.abs(float(cfg['gs_lat']))
        latitude = str(latitude) + 'N' if cfg['gs_lat'] > 0 else 'S'
        
        longitude = np.abs(float(cfg['gs_long']))
        longitude = str(longitude) + ' E' if cfg['gs_long'] > 0 else ' W'
        
        ground_station = Topos(latitude, longitude)
        difference = satellite - ground_station
        
        topocentric = difference.at(t)
        
        alt, az, distance = topocentric.altaz()
    
        if alt.degrees >= 0 and sat not in tweeted:
            el = (0, '')
            for tp in trange:
                diff = satellite - ground_station
                diff = diff.at(tp)
                elv = float(diff.altaz()[0].degrees)
                if elv > el[0]:
                    el = (elv, tp.astimezone(local_time).strftime("%I:%M:%S %p"))
                    
            pos = satellite.at(trange)
            path = pos.subpoint()

            plt.clf()
            
            map = Basemap(projection="ortho", lat_0=cfg['gs_lat'], lon_0=cfg['gs_long'], resolution='l')
        
            # draw lat/lon grid lines every 30 degrees.
            map.drawmeridians(np.arange(0,360,30))
            map.drawparallels(np.arange(-90,90,30))
            map.drawmapboundary(fill_color="navy")
            map.drawcoastlines()
            map.fillcontinents(color='darkgreen', lake_color='navy')
            
            print("Tweeted about {}".format(sat))
            
            lon = path.longitude.degrees
            lat = path.latitude.degrees
            
            map.plot(lon,lat,zorder=100,latlon=True,marker='x',color='y',markersize=2)
        
            plt.title("{} path".format(sat))
            plt.savefig('figs/{}.png'.format(sat))
            
            plt.close()
            
            tweet = "In {} minutes, {} will be over UoA! Maximum elevation is {:.2f}° at {}.".format(min_range, sat, *el)
            image = open('figs/{}.png'.format(sat), 'rb')
            
            if not silent:
                api.PostUpdate(tweet, media=image)
            
            tweeted.append(sat)

def main():
    s = sched.scheduler(time.time)
    
    iterations = 0
    reload = True
    
    def run_task():
        nonlocal iterations
        global tweeted, reload
        
        try:
            iterations += 1
            check()
            if iterations == min_range + 1:
                iterations = 0
                tweeted = []
                reload = True
        finally:
            s.enter(60, 1, run_task)
    
    run_task()
    try:
        s.run()
    except KeyboardInterrupt:
        print("Manual interrupt by user")
        return 10
    except:
        now = datetime.datetime.now()
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        print("General Exception occured at {}".format(time.now()))
        return 10

    return 0

main()