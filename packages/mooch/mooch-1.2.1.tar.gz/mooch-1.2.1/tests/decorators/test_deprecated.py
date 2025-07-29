import warnings

from mooch.decorators.deprecated import deprecated


def test_deprecated_emits_warning():
    @deprecated("use another function")
    def old_func(x):
        return x + 1

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old_func(2)
        assert result == 3
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "old_func is deprecated. use another function" in str(w[0].message)


def test_deprecated_no_reason():
    @deprecated()
    def old_func(x):
        return x * 2

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old_func(4)
        assert result == 8
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "old_func is deprecated." in str(w[0].message)


def test_deprecated_preserves_function_metadata():
    @deprecated("test")
    def foo():
        """This is foo."""
        return 42

    assert foo.__name__ == "foo"
    assert foo.__doc__ == "This is foo."
