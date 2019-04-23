from skyfield.api import Topos, load, utc
import datetime
import numpy as np
import sched, time
import sys
import utils

try:
    cfg = utils.load_config()
    api = utils.twitter_api()
    ws = utils.worksheet()
    
except utils.ValidationError as e:
    print(e)
    sys.exit(1)

tweeted = []

def check(should_reload):
    if should_reload:
        sats = utils.fetch_tracked_satellites()

    for i in range(len(sats)):
        ts = load.timescale()
        now = datetime.datetime.utcnow()
        mtime = now + datetime.timedelta(minutes=int(cfg['minutes_to_predict']))
        
        times = []
        for s in range(0, 60*int(cfg['minutes_to_predict'])):
            dtime = now + datetime.timedelta(seconds=int(s))
            times.append(ts.utc(dtime.replace(tzinfo=utc)))
        
        sat = sats[i].strip().upper()
        t = ts.utc(mtime.replace(tzinfo=utc))
        
        secs = np.arange(1, 60*(int(cfg['minutes_to_predict'])+15))
        
        trange = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second+secs)
        
        stations_url = 'http://celestrak.com/NORAD/elements/{}'.format(cfg['celestrak_file'])
        satellites = load.tle(stations_url, reload=should_reload)
        
        if should_reload:
            should_reload = False
        
        if sat not in satellites:
            continue
        
        satellite = satellites[sat]
        
        latitude = utils.format_on_sign(cfg['gs_lat'], 'N', 'S')
        longitude = utils.format_on_sign(cfg['gs_long'], 'E', 'W')
        
        ground_station = Topos(latitude, longitude)
        difference = satellite - ground_station
        
        topocentric = difference.at(t)
        
        alt, az, distance = topocentric.altaz()
    
        if alt.degrees >= int(cfg['elevation_threshold']) and sat not in tweeted:
            el = utils.compute_maximum_elevation(satellite, ground_station, trange)

            pos = satellite.at(trange)
            path = pos.subpoint()

            plot = utils.construct_image(satellite, path, ground_station, sat, times)
            plot.savefig('figs/{}.png'.format(sat))
            
            plot.show()
            
            tweet = cfg['tweet'].format(cfg['minutes_to_predict'], sat, *el)
            image = open('figs/{}.png'.format(sat), 'rb')
            
            if not cfg['silent']:
                api.PostUpdate(tweet, media=image)
                print("Tweeted about {}".format(sat))
            else:
                print(tweet)
            
            tweeted.append(sat)

def main():
    s = sched.scheduler(time.time)
    
    iterations = 0
    should_reload = True
    
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