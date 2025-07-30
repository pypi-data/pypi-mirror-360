import astrodynx as adx


def test_import() -> None:
    assert adx is not None


class TestVersion:
    def test_version(self) -> None:
        assert hasattr(adx, "__version__")
        assert isinstance(adx.__version__, str)
        assert len(adx.__version__) > 0

    def test_version_tuple(self) -> None:
        assert hasattr(adx, "__version_tuple__")
        assert isinstance(adx.__version_tuple__, tuple)
        assert len(adx.__version_tuple__) > 0
        assert all(isinstance(x, (int, str)) for x in adx.__version_tuple__)

    def test_version_aliases(self) -> None:
        assert adx.version == adx.__version__
        assert adx.version_tuple == adx.__version_tuple__
