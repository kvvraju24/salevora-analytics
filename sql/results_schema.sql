-- Tables for model results (Phases 4 and 5).
-- `python -m salevora.forecast` drops and recreates them on every run, so
-- they always hold the latest run. They have no foreign keys, so reloading
-- the raw data (sql/schema.sql) never has to touch them.

DROP TABLE IF EXISTS model_metrics;
DROP TABLE IF EXISTS holdout_predictions;
DROP TABLE IF EXISTS forecasts;
DROP TABLE IF EXISTS shap_global;
DROP TABLE IF EXISTS shap_store;

-- One row per model: its scores on the 48 held-out days (open days only).
CREATE TABLE model_metrics (
    model          VARCHAR(20) NOT NULL PRIMARY KEY,
    mae            DOUBLE      NOT NULL,
    rmse           DOUBLE      NOT NULL,
    wape           DOUBLE      NOT NULL,
    rmspe          DOUBLE      NOT NULL,
    seconds        DOUBLE      NOT NULL,  -- time to train and predict
    is_best        BOOLEAN     NOT NULL,
    holdout_start  DATE        NOT NULL,
    holdout_end    DATE        NOT NULL,
    holdout_rows   INT         NOT NULL,
    trained_at     DATETIME    NOT NULL
);

-- Every model's prediction for every open held-out store-day, next to the actual sales.
CREATE TABLE holdout_predictions (
    model      VARCHAR(20)       NOT NULL,
    store_id   SMALLINT UNSIGNED NOT NULL,
    sale_date  DATE              NOT NULL,
    actual     INT               NOT NULL,
    predicted  DOUBLE            NOT NULL,
    PRIMARY KEY (model, store_id, sale_date)
);

-- The 48-day forecast. 0 on days the store is scheduled to be closed.
CREATE TABLE forecasts (
    model            VARCHAR(20)       NOT NULL,
    store_id         SMALLINT UNSIGNED NOT NULL,
    forecast_date    DATE              NOT NULL,
    predicted_sales  DOUBLE            NOT NULL,
    PRIMARY KEY (model, store_id, forecast_date)
);

-- How much each feature moves the forecasts on average (mean absolute SHAP value).
CREATE TABLE shap_global (
    feature        VARCHAR(40) NOT NULL PRIMARY KEY,
    label          VARCHAR(80) NOT NULL,
    mean_abs_shap  DOUBLE      NOT NULL,
    model          VARCHAR(20) NOT NULL
);

-- Why one store's forecast is what it is: SHAP values for its first open forecast day.
-- base_value + SUM(shap_value) = log(1 + predicted sales).
CREATE TABLE shap_store (
    store_id       SMALLINT UNSIGNED NOT NULL,
    forecast_date  DATE              NOT NULL,
    feature        VARCHAR(40)       NOT NULL,
    label          VARCHAR(80)       NOT NULL,
    feature_value  DOUBLE            NOT NULL,
    shap_value     DOUBLE            NOT NULL,
    base_value     DOUBLE            NOT NULL,
    PRIMARY KEY (store_id, feature)
);
