from mpl_toolkits.basemap import Basemap
from skyfield.api import Topos, load, utc
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sched, time
from pytz import timezone
import sys
import utils

try:
    cfg = utils.load_config()
    api = utils.twitter_api()
    ws = utils.worksheet()
    
    sats = utils.fetch_tracked_satellites()
    
    local_time = timezone(cfg['gs_tz'])
except utils.ValidationError as e:
    print(e)
    sys.exit(1)

tweeted = []

def check():
    for i in range(len(sats)):
        now = datetime.datetime.utcnow()
        mtime = now + datetime.timedelta(minutes=cfg['minutes_to_predict'])
        
        sat = sats[i].strip().upper()
        
        ts = load.timescale()
        t = ts.utc(mtime.replace(tzinfo=utc))
        
        secs = np.arange(1, 60*(cfg['minutes_to_predict']+15))
        
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
            
            lon = path.longitude.degrees
            lat = path.latitude.degrees
            
            map.plot(lon,lat,zorder=100,latlon=True,marker='x',color='y',markersize=2)
        
            plt.title("{} path".format(sat))
            plt.savefig('figs/{}.png'.format(sat))
            
            plt.close()
            
            tweet = cfg['tweet'].format(cfg['minutes_to_predict'], sat, *el)
            image = open('figs/{}.png'.format(sat), 'rb')
            
            if not cfg['silent']:
                api.PostUpdate(tweet, media=image)
                
            print("Tweeted about {}".format(sat))
            
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
            if iterations == cfg['minutes_to_predict'] + 1:
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