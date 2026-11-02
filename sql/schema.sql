-- Tables for the raw Rossmann data (Phase 1).
-- Running this file drops and recreates them, so the load can be repeated.
-- The forecasts and model_metrics tables are added in Phase 4.

DROP TABLE IF EXISTS sales_history;
DROP TABLE IF EXISTS forecast_schedule;
DROP TABLE IF EXISTS stores;

-- One row per store (store.csv).
-- NULL means "unknown" (competition data) or "not applicable"
-- (Promo2 fields for stores that don't run Promo2).
CREATE TABLE stores (
    store_id                      SMALLINT UNSIGNED NOT NULL PRIMARY KEY,
    store_type                    CHAR(1)     NOT NULL,  -- a, b, c or d
    assortment                    CHAR(1)     NOT NULL,  -- a = basic, b = extra, c = extended
    competition_distance          INT         NULL,      -- metres to the nearest competitor
    competition_open_since_month  TINYINT     NULL,
    competition_open_since_year   SMALLINT    NULL,
    promo2                        BOOLEAN     NOT NULL,  -- takes part in the recurring promotion
    promo2_since_week             TINYINT     NULL,
    promo2_since_year             SMALLINT    NULL,
    promo_interval                VARCHAR(20) NULL       -- months Promo2 restarts, e.g. 'Jan,Apr,Jul,Oct'
);

-- One row per store per day of history (train.csv).
CREATE TABLE sales_history (
    store_id        SMALLINT UNSIGNED NOT NULL,
    sale_date       DATE     NOT NULL,
    day_of_week     TINYINT  NOT NULL,  -- 1 = Monday ... 7 = Sunday
    sales           INT      NOT NULL,  -- 0 on closed days
    customers       INT      NOT NULL,
    is_open         BOOLEAN  NOT NULL,
    promo           BOOLEAN  NOT NULL,
    state_holiday   CHAR(1)  NOT NULL,  -- 0 = none, a = public, b = Easter, c = Christmas
    school_holiday  BOOLEAN  NOT NULL,
    PRIMARY KEY (store_id, sale_date),
    INDEX idx_sales_history_date (sale_date),
    FOREIGN KEY (store_id) REFERENCES stores (store_id)
);

-- One row per store per future day to forecast (test.csv).
-- There is no sales column: that is what the model will predict.
CREATE TABLE forecast_schedule (
    kaggle_id       INT      NOT NULL UNIQUE,  -- the Id column from test.csv
    store_id        SMALLINT UNSIGNED NOT NULL,
    forecast_date   DATE     NOT NULL,
    day_of_week     TINYINT  NOT NULL,
    is_open         BOOLEAN  NULL,      -- unknown for 11 rows (store 622)
    promo           BOOLEAN  NOT NULL,
    state_holiday   CHAR(1)  NOT NULL,
    school_holiday  BOOLEAN  NOT NULL,
    PRIMARY KEY (store_id, forecast_date),
    INDEX idx_forecast_schedule_date (forecast_date),
    FOREIGN KEY (store_id) REFERENCES stores (store_id)
);
