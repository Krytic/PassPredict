import time
import twitter
import arrow
import requests
import os, random
from orbit_predictor.sources import EtcTLESource
from orbit_predictor.locations import NZ2
from orbit_predictor.predictors.base import Position
import configparser
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

plt.ioff()
plt.rcParams["font.family"] = "serif"

config = configparser.ConfigParser()
config.read("config.ini")

def get_tracked_satellites():
    url = config['tracking']['update_url']

    r = requests.get(url)

    sats = []

    for line in r.text.split("\n"):
        line = line.strip()
        if line != '':
            sats.append(line)

    return sats

def download_TLEs():
    """
    Download the TLE files from celestrak.

    Returns
    -------
    None.

    """
    url = "http://celestrak.com/NORAD/elements/active.txt"

    r = requests.get(url)

    lines = r.text.split("\r\n")

    for i in range(0, len(lines)-3, 3):
        satname = lines[i].strip()

        invalid_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

        fname = satname
        for char in invalid_chars:
            fname = fname.replace(char, "")
        line1 = satname + "\n"
        line2 = lines[i+1].strip() + "\n"
        line3 = lines[i+2].strip()
        with open(f"tles/{fname}.tle", "w") as f:
            f.writelines([line1, line2, line3])

def connect_twitter():
    """
    Generate a connection to the twitter API.

    Raises
    ------
    Exception
        If the validation with twitter failed.
        Typically this is due to an incorrect consumer key, etc.

    Returns
    -------
    api : twitter.api.Api
        An instance of the twitter API.

    """
    global config

    api = twitter.Api(**config['twitter_api'])

    if not api.VerifyCredentials():
        raise Exception("Twitter Validation Failed.")

    return api

def tweet(apiHandler, msg, media):
    """
    Post a tweet.

    Parameters
    ----------
    apiHandler : twitter.api.Api
        An instance of the Twitter API.
    tweet : string
        The tweet to send.
    media : file
        A file pointer to an image to attach.

    Returns
    -------
    None.

    """

    apiHandler.PostUpdate(msg, media=media)

checked = dict()

@sched.scheduled_job('interval', minutes=int(config['tracking']['time_between_checks']))
def main_loop():
    """
    The main loop of PassPredict.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    """
    tracking = get_tracked_satellites()
    api = connect_twitter()

    fname = random.choice(os.listdir("tles/"))

    if time.time() - os.path.getmtime(f"tles/{fname}") > 604800: # 1 week
        download_TLEs()

    now = arrow.utcnow()

    for sat in tracking:
        source = EtcTLESource(filename=f"tles/{sat}.tle")
        predictor = source.get_predictor(sat)
        predicted_pass = predictor.get_next_pass(NZ2)

        if sat in checked.keys():
            if now > checked[sat]:
                # AOS already occured, can safely remove the sat from the list
                checked.pop(sat)
            continue

        AOS_utc = arrow.get(predicted_pass.aos)

        if AOS_utc <= now.shift(minutes=120):
            LOS_utc = arrow.get(predicted_pass.los)

            plt.figure()
            lat, long = NZ2.position_llh[0], NZ2.position_llh[1]
            ax = plt.axes(projection=ccrs.NearsidePerspective(central_longitude=long, central_latitude=lat, satellite_height=35785831/3))

            ax.stock_img()

            AOS_for_image = AOS_utc.to("Pacific/Auckland").format("DD/MM/YYYY, HH:mm:ss")

            x = []
            y = []

            for t in arrow.Arrow.range('second', AOS_utc, LOS_utc):
                pos = predictor.get_position(t)
                lat = pos.position_llh[0]
                long = pos.position_llh[1]

                x.append(long)
                y.append(lat)

            plt.plot(x, y, 'r-', transform=ccrs.Geodetic())

            plt.title(f"Pass of {sat} on {AOS_for_image}")
            plt.savefig(f"images/{sat}.png", dpi=500)

            img = open(f"images/{sat}.png", 'rb')

            AOS_nzt = AOS_utc.to("Pacific/Auckland").format("HH:mm:ss")
            max_el = predicted_pass.max_elevation_deg
            tweet(api, f"There's a pass of {sat} over UoA, with maximum elevation {max_el:.2f}°, commencing at {AOS_nzt}.", img)
            print(f"Tweeted about {sat}")

            checked[sat] = AOS_utc

sched.start()