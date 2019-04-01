from mpl_toolkits.basemap import Basemap
import twitter
from skyfield.api import Topos, load, utc
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sched, time

cfg = dict()

with open('config.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        bits = line.split('=')
        cfg[bits[0]] = bits[1].strip()

api = twitter.Api(**cfg)

if not api.VerifyCredentials():
    raise ValueError('Incorrect twitter credentials!')

with open('tracking.txt', 'r') as f:
    sats = f.readlines()

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
        
        mins = np.arange(1, min_range+30)
        
        trange = ts.utc(now.year, now.month, now.day, now.hour, mins, now.second)
        
        
        stations_url = 'http://celestrak.com/NORAD/elements/active.txt'
        satellites = load.tle(stations_url)
        satellite = satellites[sat]
        
        auckland = Topos('36.852664 S', '174.768017 E')
        difference = satellite - auckland
        
        topocentric = difference.at(t)
        
        alt, az, distance = topocentric.altaz()
    
        if alt.degrees > 0 and sat not in tweeted:
    
            path = satellite.at(trange).subpoint()
            
            plt.clf()
            
            map = Basemap(projection="kav7", lon_0=-174.7684, resolution='l')
        
            # draw lat/lon grid lines every 30 degrees.
            map.drawmeridians(np.arange(0,360,30))
            map.drawparallels(np.arange(-90,90,30))
            map.drawmapboundary(fill_color="navy")
            map.drawcoastlines()
            map.fillcontinents(color='darkgreen', lake_color='navy')
            
            print(sat)
            
            lon = path.longitude.degrees
            lat = path.latitude.degrees
            
            map.plot(lon,lat,zorder=100,latlon=True,marker='x',color='y',markersize=2)
        
            plt.title("{} path".format(sat))
            plt.savefig('figs/{}.png'.format(sat))
            
            plt.close()
            
            tweet = "In {} minutes, {} will be over UoA!".format(min_range, sat)
            image = open('figs/{}.png'.format(sat), 'rb')
            
            api.PostUpdate(tweet, media=image)
            
            tweeted.append(sat)

def main():
    s = sched.scheduler(time.time)
    
    iterations = 0
    
    def run_task():
        nonlocal iterations
        global tweeted
        try:
            iterations += 1
            check()
            if iterations == min_range + 1:
                iterations = 0
                tweeted = []
        finally:
            s.enter(60, 1, run_task)
    
    run_task()
    try:
        s.run()
    except KeyboardInterrupt:
        print("Manual interrupt by user")
        return 10

    return 0

main()