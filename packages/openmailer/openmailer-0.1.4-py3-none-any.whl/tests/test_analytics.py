from openmailer.analytics import Analytics


def test_analytics_metrics():
    a = Analytics()
    a.record("sent", "smtp1")
    a.record("failed", "smtp2")

    metrics = a.get_metrics()
    assert metrics["sent:smtp1"] == 1
    assert metrics["failed:smtp2"] == 1
