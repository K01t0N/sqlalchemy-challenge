# Import the dependencies.
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
M = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def query_to_dict(query, dict):
    i = 1
    for row in query:
        dict[i] = [row[0], row[1]]
        i += 1


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitaion():

    # finding one year before the last date of the dataset
    last_row = session.query(M.date).order_by(M.date.desc()).first()
    last_date = dt.datetime.strptime(last_row[0], "%Y-%m-%d")
    date_difference = last_date - dt.timedelta(days=365)

    # retrieving the precipitation amounts
    precipitation_query = session.query(M.date, M.prcp).\
        filter(M.date >= date_difference).\
        order_by(M.date.desc()).all()

    p_dict = {}
    query_to_dict(precipitation_query, p_dict)
    return jsonify(p_dict)

@app.route("/api/v1.0/stations")
def stations():

    # retrieiving the stations
    station_query = session.query(Stations.station, Stations.name)
    station_dict = {}
    query_to_dict(station_query, station_dict)
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():

    # finding one year before the last date for the station
    stat_last_r = session.query(
        M.date
        ).filter(
            M.station == 'USC00519281'
            ).order_by(
                M.date.desc()).first()
    
    stat_last_d = dt.datetime.strptime(stat_last_r[0], "%Y-%m-%d")
    stat_d_dif = stat_last_d - dt.timedelta(days=365)

    # retrieving the temperatures
    tobs_query = session.query(M.station, M.tobs).\
                        filter((M.station == 'USC00519281') and \
                              (M.date >= stat_d_dif)).\
                      order_by(M.date.desc())

    tobs_dict = {}
    query_to_dict(tobs_query, tobs_dict)
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start(start):

    # retrieving the temperature aggregates
    query = session.query(
        func.min(M.date),
        func.count(M.station), 
        func.min(M.tobs),
        func.max(M.tobs),
        func.avg(M.tobs)
        ).filter(M.date >= start)

    # start_dict = {'minmaxavg':[x for x in start_query[0]]}
    s = query[0]

    response = {
        'response':{
            'start date':s[0],
            'stations':s[1],
            'min':s[2],
            'max':s[3],
            'avg':s[4]
    }}

    return jsonify(response)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):

    # retrieving the temperature aggregates
    query = session.query(
        func.min(M.date),
        func.max(M.date),
        func.count(M.station), 
        func.min(M.tobs),
        func.max(M.tobs),
        func.avg(M.tobs)
    ).filter(M.date >= start, M.date <= end) # query filters are separated by a comma
    # https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.filter

    # response = {'minmaxavg':[x for x in query[0]]}

    s = query[0]

    response = {
        'response':{
            'start date':s[0],
            'end date':s[1],
            'stations':s[2],
            'min':s[3],
            'max':s[4],
            'avg':s[5]
    }}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)