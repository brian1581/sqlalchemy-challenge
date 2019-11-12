import datetime as dt
import numpy as np
import pandas as pd
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List of all returnable API routes."""
    return(
        f"(Date range from 1/1/2010 to 8/23/2017). <br><br>"
        f"Available paths: <br>"

        f"/api/v1.0/precipitation<br/>"
        f"The last year of precipation data. <br><br>"

        f"/api/v1.0/stations<br/>"
        f"List of stations <br><br>"

        f"/api/v1.0/tobs<br/>"
        f"Temp data for the last year. <br><br>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Average, high, and low temps based on a date of your choice.<br><br>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"Average, max, and min temps for a range of dates."
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return Precipitation from the last 365 days of the data."""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    final_date = last_date[0][0]
# Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.datetime.strptime(final_date, '%Y-%m-%d') - dt.timedelta(days=366)
# Perform a query to retrieve the data and precipitation scores
    rain_query = session.query(Measurement.date, Station.name, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    rain_list = [rain_query]

    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    station_list = session.query(Station.name,\
     Station.station, Station.elevation).all()

    station_l2 = []
    for station in station_list:
        row = {}
        row['Station ID'] = station[0]
        row['Name'] = station[1]
        row['Elevation'] = station[2]
        station_l2.append(row)

    return jsonify(station_l2)

@app.route("/api/v1.0/tobs")
def temps():
    """Return a list of temps for the past year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    final_date = last_date[0][0]
# Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.datetime.strptime(final_date, '%Y-%m-%d') - dt.timedelta(days=366)

    temp_query = session.query(Measurement.date, Station.name, Measurement.tobs).\
    filter(Measurement.date >= year_ago).all()

    # creates JSONified list of dictionaries
    temp_list = []
    for temp in temp_query:
        row = {}
        row['Date'] = temp[0]
        row['Station'] = temp[1]
        row['Temperature'] = int(temp[2])
        temp_list.append(row)

    return jsonify(temp_list)

@app.route('/api/v1.0/<date>/')
def date(date):
    """Return the average, high and low temp based on a given date"""
    date_query = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs),\
    func.min(Measurement.tobs)).filter(Measurement.date >= date).all()

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    final_date = last_date[0][0]

    # creates JSONified list of dictionaries
    date_list = []
    for dates in date_query:
        row = {}
        row['Date'] = date
        row['Avg Temp'] = float(dates[0])
        row['High Temp'] = float(dates[1])
        row['Low Temp'] = float(dates[2])
        date_list.append(row)

    return jsonify(date_list)

@app.route('/api/v1.0/<start>/<finish>/')
def date_range(start, finish):
    """Return the avg, high and low temps over a range of dates"""
    date_window = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs),\
    func.min(Measurement.tobs)).filter(Measurement.date >= start,\
    Measurement.date <= finish).all()

    # creates JSONified list of dictionaries
    d_range = []
    for window in date_window:
        row = {}
        row['Start Date'] = start
        row['End Date'] = finish
        row['Average Temperature'] = float(window[0])
        row['Highest Temperature'] = float(window[1])
        row['Lowest Temperature'] = float(window[2])
        d_range.append(row)

    return jsonify(d_range)

if __name__ == '__main__':
    app.run(debug=True)