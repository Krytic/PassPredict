import functools
import twitter
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import WorksheetNotFound


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


def construct_image():
    pass


def compute_maximum_elevation():
    pass
