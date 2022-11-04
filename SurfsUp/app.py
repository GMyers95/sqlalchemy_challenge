import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask time
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Start and End date format= YYYY,MM,DD"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create session
    session = Session(engine)

    # Query precip
    past_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    sel = [Measurement.date, Measurement.prcp]
    past_yr_precip = session.query(*sel).filter(Measurement.date >= past_year).order_by(Measurement.date).all()

    session.close()

    past_precip = dict(past_yr_precip)

    return jsonify(past_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    # Query stations
    sel = [Station.station]
    station = session.query(*sel).all()

    session.close()

    station_list = list(np.ravel(station))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Query tobs
    station_name = Measurement.station
    station_count = func.count(Measurement.station)
    most_active_station = session.query(station_name, station_count).group_by(station_name).order_by(station_count.desc()).first()
    past_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    sel = [Measurement.date, Measurement.tobs]
    actv_year = session.query(*sel).filter(Measurement.date >= past_year).filter(Measurement.station == most_active_station[0]).order_by(Measurement.date).all()


    session.close()

    tobs_list = dict(actv_year)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create session
    session = Session(engine)
    format = "%Y,%m,%d"
    # Query start
    start_date = dt.datetime.strptime(start, format)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    starts = session.query(*sel).filter(Measurement.date >= start_date).all()

    session.close()

    
    start_list = list(np.ravel(starts))

    return jsonify(start_list)
    
    
@app.route("/api/v1.0/<start>/<end>")
def end(start,end):
    # Create session
    session = Session(engine)
    format = "%Y,%m,%d"
    # Query end
    start_date = dt.datetime.strptime(start, format)
    end_date = dt.datetime.strptime(end, format)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    ends = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    end_list = list(np.ravel(ends))

    return jsonify(end_list)

if __name__ == "__main__":
    app.run(debug=True)
