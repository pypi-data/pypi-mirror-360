from openmailer.rate_limiter import RateLimiter


def test_rate_limiter_wait():
    limiter = RateLimiter(5)
    limiter.wait()  # Should not raise
