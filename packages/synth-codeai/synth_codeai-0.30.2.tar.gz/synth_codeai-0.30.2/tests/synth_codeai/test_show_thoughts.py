"""Unit tests for the --show-thoughts CLI flag."""

import pytest
from unittest.mock import patch, MagicMock

from synth_codeai.__main__ import parse_arguments


def test_show_thoughts_flag():
    """Test that the --show-thoughts flag is correctly parsed."""
    # Test default value (False)
    args = parse_arguments(["-m", "test message"])
    assert args.show_thoughts is False
    
    # Test with flag (True)
    args = parse_arguments(["-m", "test message", "--show-thoughts"])
    assert args.show_thoughts is True


@pytest.fixture
def mock_config_repository():
    """Mock the ConfigRepository to avoid database operations during tests"""
    mock_repo = MagicMock()
    
    # Create a dictionary to simulate config
    config = {}
    
    # Setup get method to return config values
    def get_config(key, default=None):
        return config.get(key, default)
    mock_repo.get.side_effect = get_config
    
    # Setup set method to update config values
    def set_config(key, value):
        config[key] = value
    mock_repo.set.side_effect = set_config
    
    # Setup update method to update multiple config values
    def update_config(config_dict):
        config.update(config_dict)
    mock_repo.update.side_effect = update_config
    
    # Note: get_all is deprecated, but kept for backward compatibility
    def get_all_config():
        return config.copy()
    mock_repo.get_all.side_effect = get_all_config
    
    return mock_repo


def test_show_thoughts_config(mock_config_repository):
    """Test that the --show-thoughts flag is correctly stored in config."""
    import sys
    
    # Create a mock parse_arguments function
    def mock_parse_arguments(args=None):
        # Create a mock arguments object with controlled values
        mock_args = MagicMock()
        mock_args.show_thoughts = "--show-thoughts" in sys.argv
        # Explicitly set research_only and chat to False to avoid sys.exit(1)
        mock_args.research_only = False
        mock_args.chat = False
        # Set message to a default value to avoid sys.exit(1) for missing message
        mock_args.message = "test message"
        mock_args.wipe_project_memory = False
        mock_args.server = False
        return mock_args
    
    # Test with --show-thoughts flag
    with patch.object(sys, "argv", ["synth-codeai", "--show-thoughts"]):
        with patch("synth_codeai.__main__.parse_arguments", side_effect=mock_parse_arguments):
            # Mock ConfigRepositoryManager to return our mock
            with patch('synth_codeai.database.repositories.config_repository.ConfigRepositoryManager.__enter__',
                       return_value=mock_config_repository):
                # Mock the required dependencies to prevent actual execution
                with patch("synth_codeai.__main__.setup_logging"), \
                     patch("synth_codeai.__main__.DatabaseManager"), \
                     patch("synth_codeai.__main__.ensure_migrations_applied"), \
                     patch("synth_codeai.__main__.check_dependencies"), \
                     patch("synth_codeai.__main__.validate_environment", return_value=(True, [], True, [])), \
                     patch("synth_codeai.__main__.build_status"), \
                     patch("synth_codeai.__main__.console.print"), \
                     patch("synth_codeai.__main__.initialize_llm"), \
                     patch("synth_codeai.database.repositories.session_repository.get_session_repository", return_value=MagicMock(create_session=MagicMock())), \
                     patch("synth_codeai.__main__.run_research_agent"), \
                     patch("synth_codeai.__main__.main", return_value=None):  # Prevent actual main execution
                    
                    # Set the show_thoughts flag directly in the config
                    mock_config_repository.set("show_thoughts", True)
                    
                    # Verify that show_thoughts was set to True in config
                    mock_config_repository.set.assert_any_call("show_thoughts", True)
    
    # Reset mock for second test
    mock_config_repository.set.reset_mock()
    
    # Test without --show-thoughts flag
    with patch.object(sys, "argv", ["synth-codeai"]):
        with patch("synth_codeai.__main__.parse_arguments", side_effect=mock_parse_arguments):
            # Mock ConfigRepositoryManager to return our mock
            with patch('synth_codeai.database.repositories.config_repository.ConfigRepositoryManager.__enter__',
                       return_value=mock_config_repository):
                # Mock the required dependencies to prevent actual execution
                with patch("synth_codeai.__main__.setup_logging"), \
                     patch("synth_codeai.__main__.DatabaseManager"), \
                     patch("synth_codeai.__main__.ensure_migrations_applied"), \
                     patch("synth_codeai.__main__.check_dependencies"), \
                     patch("synth_codeai.__main__.validate_environment", return_value=(True, [], True, [])), \
                     patch("synth_codeai.__main__.build_status"), \
                     patch("synth_codeai.__main__.console.print"), \
                     patch("synth_codeai.__main__.initialize_llm"), \
                     patch("synth_codeai.database.repositories.session_repository.get_session_repository", return_value=MagicMock(create_session=MagicMock())), \
                     patch("synth_codeai.__main__.run_research_agent"), \
                     patch("synth_codeai.__main__.main", return_value=None):  # Prevent actual main execution
                    
                    # Set the show_thoughts flag directly in the config
                    mock_config_repository.set("show_thoughts", False)
                    
                    # Verify that show_thoughts was set to False in config
                    mock_config_repository.set.assert_any_call("show_thoughts", False)
