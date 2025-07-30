def assert_deep(deep):
    if isinstance(deep, int):
        assert deep >= 0, "deep must be greater than or equal to 0"
