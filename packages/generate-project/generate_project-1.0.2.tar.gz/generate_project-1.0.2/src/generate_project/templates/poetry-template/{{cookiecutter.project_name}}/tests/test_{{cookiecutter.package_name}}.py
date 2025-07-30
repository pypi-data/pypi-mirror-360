"""Basic tests for {{ cookiecutter.project_name }}."""


def test_import() -> None:
    """Test that the package can be imported."""
    import {{ cookiecutter.package_name }}
    assert hasattr({{ cookiecutter.package_name }}, '__version__')


def test_version() -> None:
    """Test that version is defined."""
    from {{cookiecutter.package_name}} import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
