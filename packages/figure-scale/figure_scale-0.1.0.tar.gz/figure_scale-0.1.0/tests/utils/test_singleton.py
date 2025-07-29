from figure_scale.utils.singleton import singleton


def test_singleton():
    """Test the singleton utility."""

    @singleton
    class DummyClass:
        """Dummy class for testing"""

    object1 = DummyClass()
    object2 = DummyClass()

    assert object1 is object2
