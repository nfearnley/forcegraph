from flask import request, json, render_template
from . import app
from .database import get_db, getForceGraph

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/nodes")
def nodes():
    nick = request.args.get('nick', None)
    network = request.args.get('network', None)
    depth = request.args.get('depth', 1, type=int)

    nodes, links = getForceGraph(get_db(), nick, network, depth)
    return json.dumps({"nodes": nodes, "links": links})
