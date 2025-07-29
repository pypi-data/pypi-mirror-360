from mooch.decorators import silent


def test_silent_suppresses_exception_and_returns_none():
    @silent()
    def raise_error():
        raise ValueError("fail")

    assert raise_error() is None


def test_silent_suppresses_exception_and_returns_fallback():
    @silent(fallback="fallback_value")
    def raise_error():
        raise RuntimeError("fail")

    assert raise_error() == "fallback_value"


def test_silent_returns_function_result_when_no_exception():
    @silent(fallback="fallback_value")
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


def test_silent_passes_args_and_kwargs():
    @silent(fallback=0)
    def multiply(a, b=1):
        return a * b

    assert multiply(4, b=5) == 20


def test_silent_preserves_function_metadata():
    @silent()
    def sample_func():
        """Docstring here."""
        return 42

    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Docstring here."


def test_silent_logs_exception_when_log_exceptions_is_true(caplog):
    @silent(log_exceptions=True)
    def raise_error():
        raise ValueError("fail")

    with caplog.at_level("ERROR"):
        result = raise_error()

    assert result is None
    assert "Silent Exception in raise_error. Returning fallback value 'None'." in caplog.text
    assert "ValueError: fail" in caplog.text


def test_silent_does_not_log_exception_when_log_exceptions_is_false(caplog):
    @silent(log_exceptions=False)
    def raise_error():
        raise ValueError("fail")

    result = raise_error()

    assert result is None
    assert "Silent Exception in raise_error. Returning fallback value 'None'." not in caplog.text
    assert "ValueError: fail" not in caplog.text
