import requests

URL_BASE = "http://localhost:5000"
r = requests.post(URL_BASE+ "/games", allow_redirects=False)
print("\nCenter Robots: \n",r.headers["centerRobots"])
print("\nRobot Corner: \n",r.headers["cornerRobots"])
print("\nIncinerador: \n",r.headers["incinerator"])
print( "\nBasura: \n",r.headers["garbageCells"])
LOCATION = r.headers["Location"]

r = requests.get(URL_BASE+LOCATION)
print("\nCenter Robots: \n",r.headers["centerRobots"])
print("\nRobot Corner: \n",r.headers["cornerRobots"])
print("\nIncinerador: \n",r.headers["incinerator"])
print( "\nBasura: \n",r.headers["garbageCells"])
#print(r.headers["centerRobots"])
r = requests.get(URL_BASE+LOCATION)
#print(r.headers["centerRobots"])
print("\nCenter Robots: \n",r.headers["centerRobots"])
print("\nRobot Corner: \n",r.headers["cornerRobots"])
print("\nIncinerador: \n",r.headers["incinerator"])
print( "\nBasura: \n",r.headers["garbageCells"])