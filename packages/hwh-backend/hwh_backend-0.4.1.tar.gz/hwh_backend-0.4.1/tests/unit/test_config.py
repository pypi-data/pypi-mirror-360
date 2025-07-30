import pytest
import tomli_w

from hwh_backend.hwh_config import (
    CythonCompilerDirectives,
    CythonConfig,
    Language,
    SitePackages,
)


@pytest.fixture
def minimal_config():
    return {"language": "c", "compiler_directives": {}}


def test_basic_config(minimal_config):
    config = CythonConfig(**minimal_config)
    assert config.language == Language.C


def test_site_packages_config():
    config = CythonConfig(site_packages=SitePackages.PURELIB)
    assert config.site_packages == SitePackages.PURELIB


def test_invalid_language():
    with pytest.raises(ValueError):
        CythonConfig(language="invalid")


def test_compiler_directives_validation():
    with pytest.raises(TypeError):
        CythonCompilerDirectives(boundscheck="invalid")


def test_compiler_directives_types():
    with pytest.raises(TypeError):
        CythonCompilerDirectives(binding="not_a_bool")


def test_cython_compiler_directives_constant_language_level():
    # TODO: delete - no point of testing language level, since we only accept 3
    directives = CythonCompilerDirectives()

    # Test that language_level is constant
    assert directives.language_level == "3"
    with pytest.raises(AttributeError):
        directives.language_level = "2"

    # Test that as_dict() includes language_level
    result = directives.as_dict()
    assert "language_level" in result
    assert result["language_level"] == "3"

    # Test that private fields are not included
    assert "_language_level" not in result

    # Test that all other fields work normally
    directives.binding = True
    result = directives.as_dict()
    assert result["binding"] is True
    assert result["language_level"] == "3"  # Still present and unchanged


def test_library_config():
    """Test configuration with library settings."""
    config = CythonConfig(
        libraries=["foo", "bar"],
        library_dirs=["/usr/local/lib", "/opt/lib"],
        runtime_library_dirs=["/usr/local/lib"],
        extra_link_args=["-Wl,--no-as-needed"],
    )
    assert config.libraries == ["foo", "bar"]
    assert config.library_dirs == ["/usr/local/lib", "/opt/lib"]
    assert config.runtime_library_dirs == ["/usr/local/lib"]
    assert config.extra_link_args == ["-Wl,--no-as-needed"]


def test_library_config_defaults():
    """Test default values for library settings."""
    config = CythonConfig()
    assert config.libraries == []
    assert config.library_dirs == []
    assert config.runtime_library_dirs == []
    assert config.extra_link_args == []


def test_complete_config_with_libraries():
    """Test complete configuration including library settings."""
    config = CythonConfig(
        language=Language.CPP,
        sources=["src1.pyx", "src2.pyx"],
        exclude_dirs=["tests"],
        include_dirs=["/usr/include"],
        library_dirs=["/usr/lib"],
        runtime_library_dirs=["/usr/lib"],
        libraries=["foo"],
        extra_link_args=["-Wl,--as-needed"],
        site_packages=SitePackages.SITE,
        compiler_directives=CythonCompilerDirectives(boundscheck=False),
    )
    assert config.language == Language.CPP
    assert len(config.sources) == 2
    assert config.libraries == ["foo"]
    assert config.extra_link_args == ["-Wl,--as-needed"]
    assert not config.compiler_directives.boundscheck


def test_library_config_from_pyproject(tmp_path):
    """Test parsing library configuration from pyproject.toml."""

    from hwh_backend.parser import PyProject

    test_config = {
        "project": {"name": "test-project", "version": "0.1.0"},
        "tool": {
            "hwh": {
                "cython": {
                    "language": "c++",
                    "modules": {
                        "libraries": ["foo", "bar"],
                        "library_dirs": ["/usr/local/lib"],
                        "runtime_library_dirs": ["/usr/local/lib"],
                        "extra_link_args": ["-Wl,--no-as-needed"],
                    },
                }
            }
        },
    }

    pyproject_path = tmp_path / "pyproject.toml"
    with open(pyproject_path, "wb") as f:
        tomli_w.dump(test_config, f)

    project = PyProject(tmp_path)
    config = project.get_hwh_config().cython

    assert config.language == Language.CPP
    assert config.libraries == ["foo", "bar"]
    assert config.library_dirs == ["/usr/local/lib"]
    assert config.runtime_library_dirs == ["/usr/local/lib"]
    assert config.extra_link_args == ["-Wl,--no-as-needed"]
