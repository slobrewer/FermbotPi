PRAGMA foreign_keys = ON;
 
--DROP TABLE IF EXISTS temperature_points;
 
CREATE TABLE IF NOT EXISTS temperature_points(
    id INTEGER PRIMARY KEY,
    thermometer_serial CHAR(64),
    record_time TIMESTAMP,
    temp_celcius DECIMAL(6,3));
