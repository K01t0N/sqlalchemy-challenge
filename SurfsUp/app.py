# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
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
Measurement = Base.classes.measurement
Stations = Base.classes.stations

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
    last_row = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_row[0], "%Y-%m-%d")
    date_difference = last_date - dt.timedelta(days=365)

    # retrieving the precipitation amounts
    precipitation_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_difference).\
        order_by(Measurement.date.desc()).all()

    p_dict = {}
    query_to_dict(precipitation_query, p_dict)
    return jsonify(p_dict)

@app.route("/api/v1.0/stations")
def precipitaion():

    # retrieiving the stations
    station_query = session.query(Stations.station, Stations.name)
    station_dict = {}
    query_to_dict(station_query, station_dict)
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():

    # finding one year before the last date for the station
    station_last_row = session.query(Measurement.date).\
                               filter(Measurement.station == 'USC00519281').\
                               order_by(Measurement.date.desc()).first()
    station_last_date = dt.datetime.strptime(station_last_row[0], "%Y-%m-%d")
    station_date_difference = station_last_date - dt.timedelta(days=365)

    # retrieving the temperatures
    tobs_query = session.query(Measurement.station, Measurement.tobs).\
                        filter((Measurement.station == 'USC00519281') and \
                              (Measurement.date >= station_date_difference)).\
                      order_by(Measurement.date.desc())

    tobs_dict = {}
    query_to_dict(tobs_query, tobs_dict)
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start():

    # retrieving the temperature aggregates
    start_query = session.query(Measurement.date,
                                Measurement.station, 
                                sqlalchemy.func.min(Measurement.tobs), \
                                sqlalchemy.func.max(Measurement.tobs),  \
                                sqlalchemy.func.avg(Measurement.tobs),).\
                          filter(Measurement.date >= start)

    start_dict = {}
    i = 1
    for row in start_query:
        dict[i] = [row[0], row[1], row[2], row[3], row[4]]
        i += 1

    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def end():

    # retrieving the temperature aggregates
    end_query = session.query(Measurement.date,
                              Measurement.station, 
                              sqlalchemy.func.min(Measurement.tobs), \
                              sqlalchemy.func.max(Measurement.tobs),  \
                              sqlalchemy.func.avg(Measurement.tobs),).\
                        filter((Measurement.date >= start) and \
                              (Measurement.date <= end))

    end_dict = {}

    i = 1
    for row in end_query:
        dict[i] = [row[0], row[1], row[2], row[3], row[4]]
        i += 1

    return jsonify(end_dict)

if __name__ == '__main__':
    app.run(debug=True)