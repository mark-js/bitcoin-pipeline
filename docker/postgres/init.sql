CREATE SCHEMA staging;
CREATE SCHEMA core;

CREATE TABLE core.btcusdt (
    timestamp TIMESTAMP PRIMARY KEY,
    open DECIMAL(9,1),
    high DECIMAL(9,1),
    low DECIMAL(9,1),
    close DECIMAL(9,1),
    volume DECIMAL(15,3)
);