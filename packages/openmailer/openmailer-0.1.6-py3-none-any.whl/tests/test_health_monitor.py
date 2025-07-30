from openmailer.health_monitor import HealthMonitor


def test_health_monitor_success_failure():
    monitor = HealthMonitor()
    monitor.record_success("smtp1")
    monitor.record_failure("smtp2", Exception("error"))

    health = monitor.get_health()
    assert health["smtp1"]["status"] == "healthy"
    assert health["smtp1"]["last_error"] is None
    assert health["smtp2"]["status"] == "failed"
    assert "message" in health["smtp2"]["last_error"]



