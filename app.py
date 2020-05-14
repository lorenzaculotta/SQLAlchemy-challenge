# # Step 2 - Climate App

#Dependencies
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base= automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station= Base.classes.station
Measurement= Base.classes.measurement

#Flask setup
app= Flask(__name__)

# Flask routes

@app.route("/")
def welcome():
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end <br/>" 
        f"For /api/v1.0/start route, specify a starting date in this range: 2016-08-23 - 2017-08-23 <br/>"
        f"For /api/v1.0/start/end route, specify a starting AND an ending date in this range: 2016-08-23 - 2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     #create session and bind to engine
    session = Session(engine)
    
    #query all precipitations (data and measurement) from the year before and close session
    one_year_before= dt.date(2017,8,23) - dt.timedelta(days=365)
    one_year_before

    # Perform a query to retrieve the data and precipitation scores
    precipitation= session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= one_year_before).all()
    session.close()

    #np.ravel to create a dictionary of the results, then list() to enable jsonification
    precipitation_list= list(np.ravel(precipitation))
    
    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    #create session and bind to engine
    session= Session(engine)

    #query stations and close session
    stations= session.query(Station.station).all()
    session.close()

   #np.ravel to create a dictionary of the results, then list() to enable jsonification
    stations_list= list(np.ravel(stations))
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    #create session and bind to engine
    session= Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data.
    one_year_before= dt.date(2017,8,23) - dt.timedelta(days=365)
    
    #retrieve most active station
    active_stations=session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
    most_active_station= active_stations[0][0]

    #retrieve tobs for most_active_station. Close session
    tobs= session.query(Measurement.date, Measurement.tobs).\
          filter(Measurement.date >= one_year_before).filter(Measurement.station == most_active_station).all()
    session.close()

    #np.ravel to create a dictionary of the results, then list() to enable jsonification
    tobs_list= list(np.ravel(tobs))

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    #create session and bind to engine
    session= Session(engine)

    #Query Tmin, Tavg, Tmax for all dates greater than and equal to the start date. Close session
    sel=[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temperatures= session.query(*sel).\
            filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()

    #np.ravel to create a dictionary of the results, then list() to enable jsonification
    temperatures_list= list(np.ravel(temperatures))

    return jsonify(temperatures_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #create session and bind to engine
    session= Session(engine)

    #Query Tmin, Tavg, Tmax for all dates greater than and equal to the start date. Close session
    sel=[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temperatures= session.query(*sel).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    session.close()

    #np.ravel to create a dictionary of the results, then list() to enable jsonification
    temperatures_list= list(np.ravel(temperatures))

    return jsonify(temperatures_list)


if __name__ == '__main__':
    app.run(debug=True)
