import requests

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