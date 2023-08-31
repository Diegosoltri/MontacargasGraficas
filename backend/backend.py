import flask
from flask.json import jsonify
import json
import uuid
from cleaning_robot import Room
from GarbageCell import GarbageCell
from RobotCorner import RobotCorner
from RobotCenter import RobotCenter
from Incinerator import Incinerator

games = {}

app = flask.Flask(__name__)

def getAgents(model, garbageCells, cornerRobots, centerRobots, incinerators):
    for agent in model.schedule.agents:
        if isinstance(agent, GarbageCell):
            garbageCells.append(
                {
                    "id": agent.id,
                    "x": agent.pos[0],
                    "y": agent.pos[1],
                    "dirty": agent.dirty,
                    "burned": agent.burned,
                }
            )
        if isinstance(agent, RobotCenter):
            centerRobots.append(
                {
                    "section": agent.section,
                    "x": agent.pos[0],
                    "y": agent.pos[1],
                    "loaded": agent.loaded,
                }
            )
        if isinstance(agent, RobotCorner):
            cornerRobots.append(
                {
                    "section": agent.section,
                    "x": agent.pos[0],
                    "y": agent.pos[1],
                    "loaded": agent.loaded,
                }
            )
        if isinstance(agent, Incinerator):
            incinerators.append({"on:": agent.on})


@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    model = Room()
    games[id] = model
    garbageCells = []
    cornerRobots = []
    centerRobots = []
    incinerators = []
    getAgents(model, garbageCells, cornerRobots, centerRobots, incinerators)
    return (
        "ok",
        201,
        (
            {
                "Location": f"/games/{id}",
                "garbageCells": json.dumps(garbageCells),
                "cornerRobots": json.dumps(cornerRobots),
                "centerRobots": json.dumps(centerRobots),
                "incinerator": json.dumps(incinerators),
            }
        ),
    )


@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    garbageCells = []
    cornerRobots = []
    centerRobots = []
    incinerators = []
    getAgents(model, garbageCells, cornerRobots, centerRobots, incinerators)
    return ("ok", 500,
        {
            "garbageCells": json.dumps(garbageCells),
            "cornerRobots": json.dumps(cornerRobots),
            "centerRobots": json.dumps(centerRobots),
            "incinerator": json.dumps(incinerators),
        }
    )


app.run()
