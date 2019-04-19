import functools # Memoization decorator
import twitter # Python-Twitter API
import gspread # Spreadsheet API
from oauth2client.service_account import ServiceAccountCredentials # OAuth Wrapper
from gspread.exceptions import WorksheetNotFound

# Custom Exception Types
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
            if bits[0][:3] == "tw:":
                cfg['twitter'][bits[0][3:]] = bits[1].strip()
            else:
                cfg[bits[0]] = bits[1].strip()
    
    return cfg

def connect_twitter():
    cfg = load_config()
    api = twitter.Api(**cfg['twitter'])
    if not api.VerifyCredentials():
        raise ValidationError('Incorrect twitter credentials!')
        
    return api

def connect_sheets():
    cfg = load_config()
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive'] # API recently changed, not sure which scope is required
    
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    
    try:
        ws = client.open_by_key(cfg['sheet_id']).worksheet(cfg['sheet_name'])
    except WorksheetNotFound:
        raise ValidationError("Incorrect sheet details. Confirm that sheet_name and sheet_id are correctly set in config.txt")
    
    return ws

def construct_image():
    pass

def compute_maximum_elevation():
    pass