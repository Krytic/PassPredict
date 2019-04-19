from skyfield.api import Topos, load, utc
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sched, time
import sys
import utils

try:
    cfg = utils.load_config()
    api = utils.twitter_api()
    ws = utils.worksheet()
    
    sats = utils.fetch_tracked_satellites()
    
except utils.ValidationError as e:
    print(e)
    sys.exit(1)

tweeted = []

def check(should_reload):
    for i in range(len(sats)):
        now = datetime.datetime.utcnow()
        mtime = now + datetime.timedelta(minutes=int(cfg['minutes_to_predict']))
        
        sat = sats[i].strip().upper()
        
        ts = load.timescale()
        t = ts.utc(mtime.replace(tzinfo=utc))
        
        secs = np.arange(1, 60*(int(cfg['minutes_to_predict'])+15))
        
        trange = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second+secs)
        trange_dupe = [datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second+sec) for sec in secs]
        
        stations_url = 'http://celestrak.com/NORAD/elements/active.txt'
        satellites = load.tle(stations_url, reload=should_reload)
        
        if should_reload:
            should_reload = False
        
        if sat not in satellites:
            continue
        
        satellite = satellites[sat]
        
        latitude = np.abs(float(cfg['gs_lat']))
        latitude = str(latitude) + ' N' if float(cfg['gs_lat']) > 0 else str(latitude) + ' S'
        
        longitude = np.abs(float(cfg['gs_long']))
        longitude = str(longitude) + ' E' if float(cfg['gs_long']) > 0 else str(longitude) + ' W'
        
        ground_station = Topos(latitude, longitude)
        difference = satellite - ground_station
        
        topocentric = difference.at(t)
        
        alt, az, distance = topocentric.altaz()
    
        if alt.degrees >= 0 and sat not in tweeted:
            el = utils.compute_maximum_elevation(satellite, ground_station, trange)

            pos = satellite.at(trange)
            path = pos.subpoint()

            plot = utils.construct_image(satellite, path, trange, ground_station, sat, trange_dupe)
            plot.savefig('figs/{}.png'.format(sat))
            
            plot.show()
            
            tweet = cfg['tweet'].format(cfg['minutes_to_predict'], sat, *el)
            image = open('figs/{}.png'.format(sat), 'rb')
            
            if not cfg['silent']:
                api.PostUpdate(tweet, media=image)
                
            print("Tweeted about {}".format(sat))
            
            tweeted.append(sat)

def main():
    s = sched.scheduler(time.time)
    
    iterations = 0
    should_reload = False
    
    def run_task(should_reload):
        nonlocal iterations
        global tweeted
        
        try:
            iterations += 1
            check(should_reload)
            if iterations == int(cfg['minutes_to_predict']) + 1:
                iterations = 0
                tweeted = []
                should_reload = True
        finally:
            s.enter(60, 1, run_task)
    
    run_task(should_reload)
    
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