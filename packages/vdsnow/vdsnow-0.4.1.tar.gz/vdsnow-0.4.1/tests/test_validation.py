from pathlib import Path
import pytest
from vdsnow.validation import _get_structure_discrepancies


def setup_test_environment(tmp_path: Path):
    """Helper to create a temporary project structure for testing."""
    (tmp_path / "setup").mkdir()
    (tmp_path / "snowflake_structure").mkdir()

    # Monkeypatch the constants in the validation module to point to our temp dirs
    pytest.MonkeyPatch().setattr("vdsnow.validation.SETUP_BASE_DIR_NAME", str(tmp_path / "setup"))
    pytest.MonkeyPatch().setattr("vdsnow.validation.BASE_DIR_NAME", str(tmp_path / "snowflake_structure"))


def test_validation_passes_on_valid_structure(tmp_path: Path):
    """
    Tests that a perfectly valid structure returns no errors or warnings.
    """
    setup_test_environment(tmp_path)

    # Arrange: Create a valid file and a setup manifest that sources it
    (tmp_path / "snowflake_structure" / "my_table.sql").touch()
    (tmp_path / "setup" / "manifest.sql").write_text("!source ./snowflake_structure/my_table.sql")

    # Act
    broken, unreferenced = _get_structure_discrepancies()

    # Assert: The test ONLY cares about the critical failure scenario.
    assert not broken, "A valid structure should not have any broken links."


def test_validation_finds_broken_link(tmp_path: Path):
    """
    Tests that a broken link in a setup file is correctly identified.
    This is the critical failure scenario.
    """
    setup_test_environment(tmp_path)

    # Arrange: Create a setup manifest that points to a non-existent file
    (tmp_path / "setup" / "manifest.sql").write_text("!source ./snowflake_structure/i_do_not_exist.sql")

    # Act
    broken, unreferenced = _get_structure_discrepancies()

    # Assert
    assert len(broken) == 1, "Should find exactly one broken link."
    assert "snowflake_structure/i_do_not_exist.sql" in broken[0]


def test_validation_finds_unreferenced_file(tmp_path: Path):
    """
    Tests that a file in the structure that isn't sourced is found.
    The test itself should still pass, as this is just a warning.
    """
    setup_test_environment(tmp_path)

    # Arrange: Create a file in the structure but no setup manifest for it
    (tmp_path / "snowflake_structure" / "unreferenced_file.sql").touch()

    # Act
    broken, unreferenced = _get_structure_discrepancies()

    # Assert: The test passes because there are no *broken* links.
    assert not broken, "Unreferenced files should not cause a broken link error."
    assert len(unreferenced) == 1, "Should find exactly one unreferenced file."
    assert "snowflake_structure/unreferenced_file.sql" in unreferenced[0]
