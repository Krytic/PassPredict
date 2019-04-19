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
    pass

def connect_sheets():
    pass

def construct_image():
    pass

def compute_maximum_elevation():
    pass