name: str = "toolforge_weld"
__version__: str

try:
    from importlib.metadata import version

    __version__ = version(name)
except (ImportError, NameError):
    # Temporally fallback to pkg_resources if importlib.metadata is not available.
    # See phabricator.wikimedia.org/T370932
    from pkg_resources import get_distribution  # type: ignore[import-not-found]

    __version__ = get_distribution(name).version
except Exception:
    __version__ = "0.0.0"
