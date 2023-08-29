import requests

URL_BASE = "http://localhost:5000"
r = requests.post(URL_BASE+ "/games", allow_redirects=False)
print(r.headers["centerRobots"])
LOCATION = r.headers["Location"]
r = requests.get(URL_BASE+LOCATION)
print(r.headers["centerRobots"])
r = requests.get(URL_BASE+LOCATION)
print(r.headers["centerRobots"])