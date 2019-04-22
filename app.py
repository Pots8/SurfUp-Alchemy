# import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

from flask import Flask, jsonify
# create engine
# engine = create_engine("sqlite:///hawaii.sqlite")
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

# reflection
Base = automap_base()

Base.prepare(engine, reflect=True)

# reference the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session
session = Session(engine)

# setup flask
app = Flask(__name__)

# set route

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Climate App Homepage:<br/>"
        f"/api/v1.0/precipitations<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2017-07-28<br/>"
        f"/api/v1.0/temp/2017-07-28/2017-08-15"
    )

@app.route("/api/v1.0/precipitations")
def precipitation():
    """Query precipitation for last year"""
    # one year from the latest date
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_data_point = last_data_point[0]
    
    prev_year = dt.datetime.strptime(last_data_point,"%Y-%m-%d") - dt.timedelta(days=366)

    # Query for the date and precipitation last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precipitation

    # Dictionary with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return stations list"""
    results = session.query(Station.station).all()

    # Unravel results to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_obsv():
    """Return  temperature observations (tobs) of last year from last datapoint."""
    # find last data point and one year
    last_data_point1 = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_data_point1 = last_data_point1[0]
    
    prev_year1 = dt.datetime.strptime(last_data_point1,"%Y-%m-%d") - dt.timedelta(days=366)
  

    # find for the top station last year
    result1 = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year1).all()

    # Unravel to a list
    temps = list(np.ravel(result1))

    # Return the results
    return jsonify(temps)

 
@app.route("/api/v1.0/temp/<start>")

# Return list of min, avg, max from the start date

def startdt(start=None):

    given_start= session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).group_by(Measurement.date).all()

    given_start_list = list(np.ravel(given_start))
    return jsonify(given_start_list)




@app.route("/api/v1.0/temp/<start>/<end>")


def start_enddt(start=None, end=None):

    given_se= session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    given_se_list = list(np.ravel(given_se))
    return jsonify(given_se_list)



if __name__ == '__main__':
    app.run(debug=True)