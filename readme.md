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

    tw:consumer_key=<CONSUMER_KEY>
    tw:consumer_secret=<CONSUMER_SECRET>
    tw:access_token_key=<TOKEN>
    tw:access_token_secret=<SECRET_KEY>

You will also need a `client_secret.json` file from the Google APIs spreadsheet. Any sheet is permissable via the following settings in `config.txt`:

    sheet_id=<SHEET_ID>
    sheet_name=<SHEET_NAME>
    
You must configure your ground station also (PassPredict assumes +/+ lat/long for N/E, and -/- for S/W):

    gs_lat=<LATITUDE>
    gs_long=<LONGITUDE>
    gs_tz=<TIMEZONE_STRING>

To run, invoke it from the command line:

    python PassPredict.py [mode] [silent]
    
Where `mode` is either `dynamic` (loads from google sheet) or `normal` (loads from file), and `silent` is either `silent` (does not tweet) or `speak` (tweets). If you wish to specify one option, you must specify both.

PassPredict will test your credentials and refuse to run if they are correct. By default PassPredict runs every 60 seconds (customisable, although is hardcoded in).

## Branch Policy
Master is considered to be bleeding-edge. Releases are tagged, please make changes on different branches and we will merge them to master as required.

We follow the [major.minor.patch](https://semver.org/) version schema, which will be introduced with version 1.0.0 (and will be tagged as such). Until then, consider this alpha software, or if you prefer a concrete version number, 0.1.0.