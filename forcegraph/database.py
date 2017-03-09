from flask import g
from . import app
import sqlite3

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def getForceGraph(conn, nick, network, depth=1):
    c = conn.cursor()
    c.row_factory = lambda cursor, row: row[0]

    # Get NickId
    nickid = c.execute("SELECT NickId FROM Nick WHERE Nick.Nick = ? ", (nick, )).fetchone()
    if nickid is None:
        raise ValueError("nick not found")
    # Get NetworkId
    networkid = c.execute("SELECT NetworkId FROM Network WHERE Network.NetworkName = ? ", (network, )).fetchone()
    if networkid is None:
        raise ValueError("network not found")

    return getForceGraphById(conn, nickid, networkid, depth)

def getForceGraphById(conn, nickid, networkid, depth=1):
    c = conn.cursor()

    # Create source data table
    c.execute("DROP TABLE IF EXISTS NickLink; ")
    c.execute("CREATE TEMPORARY TABLE NickLink "
    "AS "
    "SELECT NetworkId, Source, Target, COUNT(*) AS LinkCount "
    "FROM "
    "( "
    "    SELECT "
    "        NetworkId, "
    "        OldNickId AS Source, "
    "        NewNickId AS Target "
    "    FROM LogNick "
    "    INNER JOIN LogEvent "
    "        ON LogNick.LogEventId == LogEvent.LogEventId "
    "    UNION ALL "
    "    SELECT "
    "        NetworkId, "
    "        NewNickId AS Source, "
    "        OldNickId AS Target "
    "    FROM LogNick "
    "    INNER JOIN LogEvent "
    "        ON LogNick.LogEventId == LogEvent.LogEventId "
    ") "
    "GROUP BY NetworkId, Source, Target; ")

    # Create temporary table for recursive joins
    c.execute("DROP TABLE IF EXISTS LinkLookup; ")
    c.execute("CREATE TEMPORARY TABLE LinkLookup (NickId PRIMARY KEY); ")

    # Insert starting NickId
    c.execute("INSERT INTO LinkLookup (NickId) VALUES (?); ", (nickid, ))

    # Follow links recursively to find all attached nodes, stop after given number of iterations, or after finding all possible nodes.
    for _ in range(depth-1):
        c.execute(
            "INSERT OR IGNORE INTO LinkLookup "
            "SELECT Target "
            "FROM "
            "    NickLink "
            "    INNER JOIN LinkLookup "
            "        ON NickLink.Source = LinkLookup.NickId "
            "WHERE NetworkId = ?; ",  # Filter based on network
            (networkid, ))
        if not c.rowcount:
            break

    c.row_factory = sqlite3.Row

    # Select all found links
    links = [dict(link) for link in c.execute(
        "SELECT Source as source, Target as target, LinkCount as linkcount "
        "FROM LinkLookup "
        "    INNER JOIN NickLink "
        "        ON LinkLookup.NickId = NickLink.Source "
        "WHERE NetworkId = ?; ",  # Filter based on network
        (networkid, )).fetchall()]

    # Append nodes attached to edge links
    c.execute(
        "INSERT OR IGNORE INTO LinkLookup "
        "SELECT Target "
        "FROM "
        "    NickLink "
        "    INNER JOIN LinkLookup "
        "        ON NickLink.Source = LinkLookup.NickId "
        "WHERE NetworkId = ?; ",  # Filter based on network
        (networkid, ))

    # Select all found Nick nodes
    nodes = [dict(name) for name in c.execute(
        "SELECT Nick.NickId as nickid, Nick.Nick as nick "
        "FROM "
        "    LinkLookup "
        "    INNER JOIN Nick "
        "        ON LinkLookup.NickId = Nick.NickId; ").fetchall()]

    return nodes, links
