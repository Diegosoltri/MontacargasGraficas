import requests
import json  # Import the json module

URL_BASE = "http://localhost:5000"
r = requests.post(URL_BASE + "/games", allow_redirects=False)
# print("\nCenter Robots: \n", r.headers["centerRobots"])
# print("\nRobot Corner: \n", r.headers["cornerRobots"])
# print("\nIncinerador: \n", r.headers["incinerator"])
# print( "\nBasura: \n",r.headers["garbageCells"])
LOCATION = r.headers["Location"]

# Parse the JSON strings into Python lists
centerRobots = json.loads(r.headers["centerRobots"])
cornerRobots = json.loads(r.headers["cornerRobots"])
incinerator = json.loads(r.headers["incinerator"])
garbageCells = json.loads(r.headers["garbageCells"])

# print(garbageCells)
# print(len(garbageCells))

print(incinerator)

# for r in centerRobots:
#     x,z = r['x']*10 - DimBoard, r['z']*10 - DimBoard
#     print((x,z))

# for i in range(4):
#     print(cornerRobots[i])

r = requests.get(URL_BASE+LOCATION)

# Parse the JSON strings into Python lists
# centerRobots = json.loads(r.headers["centerRobots"])
# cornerRobots = json.loads(r.headers["cornerRobots"])
# incinerator = json.loads(r.headers["incinerator"])
# garbageCells = json.loads(r.headers["garbageCells"])

# print(garbageCells)
# print(len(garbageCells))
# print("\n")

# for r in centerRobots:
#     print(r)
    
# for i in range(4):
#     sect = cornerRobots[i]['section']
#     if sect == 0 or sect == 1:
#         xStep = -DimBoard
#     else: 
#         xStep = DimBoard
#     if sect == 0 or sect == 3:
#         zStep = -DimBoard
#     else: 
#         zStep = DimBoard
#     print(xStep, zStep)

# r = requests.get(URL_BASE+LOCATION)
# print("\nCenter Robots: \n",r.headers["centerRobots"])
# print("\nRobot Corner: \n",r.headers["cornerRobots"])
# print("\nIncinerador: \n",r.headers["incinerator"])
# print( "\nBasura: \n",r.headers["garbageCells"])
# #print(r.headers["centerRobots"])
# r = requests.get(URL_BASE+LOCATION)
# #print(r.headers["centerRobots"])
# print("\nCenter Robots: \n",r.headers["centerRobots"])
# print("\nRobot Corner: \n",r.headers["cornerRobots"])
# print("\nIncinerador: \n",r.headers["incinerator"])
# print( "\nBasura: \n",r.headers["garbageCells"])