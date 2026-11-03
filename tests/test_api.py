"""Phase 7 checks: the API answers correctly and rejects bad input."""
import pytest
from fastapi.testclient import TestClient

from api.main import app
from salevora.db import has_db_settings

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")
client = TestClient(app)


def test_health_names_the_best_model():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["best_model"] in {"XGBoost", "LightGBM", "Random Forest", "Ridge", "Baseline"}


def test_stores_list_is_complete_and_json_safe():
    stores = client.get("/stores").json()
    assert len(stores) == 1_115
    assert sum(s["competition_distance"] is None for s in stores) == 3  # blanks become null


def test_forecast_for_all_stores_and_one_store():
    chain = client.get("/forecast").json()
    assert len(chain["days"]) == 48 and "typical_error" not in chain
    store = client.get("/forecast", params={"store_id": 1}).json()
    assert len(store["days"]) == 48 and store["typical_error"] > 0


def test_history_respects_days():
    assert len(client.get("/history", params={"store_id": 1, "days": 14}).json()) == 14


@pytest.mark.parametrize("path, params, status", [
    ("/history", {"days": 3}, 422),               # too few days
    ("/history", {"store_id": -1}, 422),          # negative store
    ("/history", {"store_id": 9999}, 404),        # unknown store
    ("/forecast", {"store_id": 2}, 404),          # history but no forecast schedule
    ("/forecast", {"model": "Magic"}, 422),       # unknown model
    ("/explain/0", {}, 422),                      # explanations are per store
])
def test_bad_requests_are_rejected(path, params, status):
    assert client.get(path, params=params).status_code == status


def test_explanations():
    assert len(client.get("/explain").json()) == 17
    assert len(client.get("/explain/1").json()) == 17
