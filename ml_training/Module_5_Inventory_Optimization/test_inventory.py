"""Unit tests for Module 5 — Inventory Optimization."""
import pytest
try:
    from inventory_optimizer import optimize_inventory
except ImportError:
    from ml_training.Module_5_Inventory_Optimization.inventory_optimizer import optimize_inventory


def test_critical_stock():
    result = optimize_inventory({
        "current_stock": 10,
        "forecast_daily_demand": 20,
        "lead_time_days": 5,
        "safety_stock_days": 3
    })
    assert result["status"] == "CRITICAL_REPLENISH"
    assert result["recommended_order_quantity"] > 0
    assert result["safety_stock_units"] == 60.0
    assert result["reorder_point"] == 160.0


def test_healthy_stock():
    result = optimize_inventory({
        "current_stock": 500,
        "forecast_daily_demand": 20,
        "lead_time_days": 5,
        "safety_stock_days": 3,
        "review_period_days": 7
    })
    assert result["status"] == "HEALTHY"
    assert result["recommended_order_quantity"] == 0


def test_replenish_stock_with_pack_size():
    result = optimize_inventory({
        "current_stock": 100,
        "forecast_daily_demand": 20,
        "lead_time_days": 5,
        "safety_stock_days": 3,
        "review_period_days": 7,
        "pack_size": 25
    })
    assert result["status"] == "REPLENISH"
    # Target stock = 20 * (5 + 3 + 7) = 300. Deficit = 200. Pack multiple of 25 = 200.
    assert result["recommended_order_quantity"] == 200
    assert result["recommended_order_quantity"] % 25 == 0


def test_boundary_zero_stock():
    result = optimize_inventory({
        "current_stock": 0,
        "forecast_daily_demand": 10,
        "lead_time_days": 3,
        "safety_stock_days": 2,
    })
    assert result["status"] == "CRITICAL_REPLENISH"
    assert result["recommended_order_quantity"] > 0


def test_invalid_negative_stock():
    with pytest.raises(ValueError, match="cannot be negative"):
        optimize_inventory({
            "current_stock": -5,
            "forecast_daily_demand": 10,
            "lead_time_days": 3
        })


def test_invalid_zero_pack_size():
    with pytest.raises(ValueError, match="pack_size must be greater than zero"):
        optimize_inventory({
            "current_stock": 50,
            "forecast_daily_demand": 10,
            "lead_time_days": 3,
            "pack_size": 0
        })


def test_missing_demand():
    with pytest.raises(ValueError, match="Missing required field"):
        optimize_inventory({
            "current_stock": 50,
            "lead_time_days": 3
        })


if __name__ == "__main__":
    test_critical_stock()
    test_healthy_stock()
    test_replenish_stock_with_pack_size()
    test_boundary_zero_stock()
    print("All Module 5 unit tests passed.")
