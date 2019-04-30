# PassPredict

Intelligent twitter bot to track and identify satellites that are passing overhead. Follow it on twitter at [@passpredict](http://twitter.com/passpredict)

## Installation and dependencies
PassPredict requires the following libraries:
- Anaconda (Numpy, Matplotlib + Basemap, Scipy)
- [Skyfield](https://rhodesmill.org/skyfield)
- [Python-Twitter](https://github.com/bear/python-twitter)
- gspread
- oauth2client
- pytz

To install, download a fork into your folder. Create a file called `config.txt` with the following contents. You may use # at the BEGINNING of a line as a comment, and empty lines are ignored.


    #####################################
    ## Pass Predict Configuration File ##
    #####################################
    
    ## Twitter Configuration ##
    twitter:consumer_key=<CONSUMER KEY>                                             # Consumer Key
    twitter:consumer_secret=<CONSUMER SECRET>                                       # Consumer Secret
    twitter:access_token_key=<TOKEN KEY>                                            # Access Token Key
    twitter:access_token_secret=<TOKEN SECRET>                                      # Access Token Secret
    twitter_meta:user=<TWITTER USERNAME>                                            # User to DM if bot goes down
    
    ## Ground Station Information ##
    gs:lat=<LAT>                                                                    # Latitude of the Ground Station
    gs:long=<LONG>                                                                  # Longitude of the Ground Station
    gs:tz=Pacific/Auckland                                                          # pytz-compatible timezone of the Ground Station
    
    ## Google Sheet Information ##
    sheet:id=<SHEET ID>                                                             # Sheet ID of the satellite list
    sheet:name=<SHEET NAME>                                                         # Worksheet Name of the satellite list
    sheet:logsheet_name=<SHEET NAME>                                                # Worksheet Name of the tracking log
    
    ## Running Options ##
    run_mode=normal                                                                 # Whether to run the bot in normal (from file) mode or dynamic (from sheet) mode
    silent=True                                                                     # True: Does not tweet. False: Tweets
    minutes_to_predict=15                                                           # How far ahead the bot should predict
    elevation_threshold=0                                                           # How far above the horizon (degs) a pass should be to be considered tweet-worthy
    tweet=In {} minutes, {} will be over UoA! Maximum elevation is {:.2f}° at {}.   # The content of the tweet.
    
    ## Celestrak Information ##
    celestrak_file=active.txt                                                       # The celestrak filename of the TLE files.
    
    ## Run in debug mode? ##
    debug=True

To run, invoke it from the command line:

    nohup python PassPredict.py & 

(This runs it as a background process, use `ps aux | grep PassPredict` to monitor it)

PassPredict will test your credentials and refuse to run if they are correct. By default PassPredict runs every 60 seconds (customisable, although is hardcoded in).

## Branch Policy
Master is considered to be bleeding-edge. Releases are tagged, please make changes on different branches and we will merge them to master as required.

We follow the [major.minor.patch](https://semver.org/) version schema, which will be introduced with version 1.0.0 (and will be tagged as such). Until then, consider this alpha software, or if you prefer a concrete version number, 0.1.0.
