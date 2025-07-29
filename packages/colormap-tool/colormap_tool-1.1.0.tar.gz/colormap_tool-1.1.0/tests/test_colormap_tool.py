def test_import():
    """Test import of the package."""
    try:
        import colormap_tool
    except ImportError:
        assert False, "Could not import the package"
    else:
        assert True, "Package imported successfully"
