"""
CLI tests for wtu-mlflow-triton-plugin

This module contains comprehensive tests for the keynet CLI commands,
including both basic functionality and edge cases.
"""

import json
import sys
from argparse import Namespace
from unittest.mock import MagicMock, patch

import pytest

# Import the functions we need
from keynet_inference.cli.main import (
    deploy_command,
    handle_test_command,
    login_command,
    logout_command,
    main,
)

cli_main = sys.modules["keynet_inference.cli.main"]


class TestCLI:
    """Comprehensive CLI tests including edge cases"""

    @pytest.fixture
    def mock_args(self):
        """Mock argparse.Namespace"""
        return Namespace()

    # ==================== Login Command Tests ====================

    def test_login_command_success(self, tmp_path, mock_args):
        """Test successful login command"""
        mock_args.server_domain = "api.keynet.io"

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch("builtins.input", return_value="testuser"):
                with patch("getpass.getpass", return_value="testpass"):
                    with patch.object(cli_main, "AuthClient") as mock_auth:
                        with patch.object(cli_main, "CredentialManager") as mock_cred:
                            mock_auth.return_value.authenticate.return_value = (
                                True,
                                "mock-token",
                            )
                            result = login_command(mock_args)

                            assert result == 0
                            mock_cred.return_value.save_credentials.assert_called_with(
                                "api.keynet.io", "testuser", "testpass"
                            )

    def test_login_empty_username(self, mock_args):
        """Test login with empty username"""
        mock_args.server_domain = "api.keynet.io"

        with patch("builtins.input", return_value=""):
            result = login_command(mock_args)

        assert result == 1

    def test_login_empty_password(self, mock_args):
        """Test login with empty password"""
        mock_args.server_domain = "api.keynet.io"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value=""):
                result = login_command(mock_args)

        assert result == 1

    def test_login_with_protocol_stripping(self, mock_args):
        """Test login strips http/https protocol"""
        # Test with http://
        mock_args.server_domain = "http://api.keynet.io"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value="testpass"):
                with patch.object(cli_main, "AuthClient") as mock_auth:
                    with patch.object(cli_main, "CredentialManager") as mock_cred:
                        mock_auth.return_value.authenticate.return_value = (
                            True,
                            "token",
                        )
                        login_command(mock_args)

                        # Should be called with domain without protocol
                        mock_auth.assert_called_with("api.keynet.io")
                        mock_cred.return_value.save_credentials.assert_called_with(
                            "api.keynet.io", "testuser", "testpass"
                        )

        # Test with https://
        mock_args.server_domain = "https://secure.keynet.io"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value="testpass"):
                with patch.object(cli_main, "AuthClient") as mock_auth:
                    with patch.object(cli_main, "CredentialManager") as mock_cred:
                        mock_auth.return_value.authenticate.return_value = (
                            True,
                            "token",
                        )
                        login_command(mock_args)

                        mock_auth.assert_called_with("secure.keynet.io")
                        mock_cred.return_value.save_credentials.assert_called_with(
                            "secure.keynet.io", "testuser", "testpass"
                        )

    def test_login_authentication_failure(self, mock_args):
        """Test login with authentication failure"""
        mock_args.server_domain = "api.keynet.io"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value="wrongpass"):
                with patch.object(cli_main, "AuthClient") as mock_auth:
                    with patch.object(cli_main, "CredentialManager"):
                        mock_auth.return_value.authenticate.return_value = (
                            False,
                            "Invalid credentials",
                        )
                        result = login_command(mock_args)

                        assert result == 1

    # ==================== Logout Command Tests ====================

    def test_logout_command_show_credentials(self, tmp_path, mock_args):
        """Test logout command showing current credentials"""
        mock_args.all = False
        mock_args.server = None

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch.object(cli_main, "CredentialManager") as mock_cred:
                mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
                mock_cred.return_value.get_credentials.return_value = (
                    "testuser",
                    "testpass",
                )

                result = logout_command(mock_args)

        assert result == 0

    def test_logout_all_servers(self, mock_args):
        """Test logout --all option"""
        mock_args.all = True
        mock_args.server = None

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            result = logout_command(mock_args)

        assert result == 0
        mock_cred.return_value.remove_credentials.assert_called_with()

    def test_logout_specific_server(self, mock_args):
        """Test logout with specific server"""
        mock_args.all = False
        mock_args.server = "api.keynet.io"

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = [
                "api.keynet.io",
                "staging.keynet.io",
            ]
            result = logout_command(mock_args)

        assert result == 0
        mock_cred.return_value.remove_credentials.assert_called_with("api.keynet.io")

    def test_logout_nonexistent_server(self, mock_args):
        """Test logout with non-existent server"""
        mock_args.all = False
        mock_args.server = "nonexistent.keynet.io"

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            result = logout_command(mock_args)

            assert result == 1

    def test_logout_no_saved_credentials(self, mock_args):
        """Test logout when no credentials are saved"""
        mock_args.all = False
        mock_args.server = None

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = []
            result = logout_command(mock_args)

        assert result == 0

    # ==================== Test Command Tests ====================

    def test_test_command_success(self, mock_args, valid_python_file):
        """Test command successful validation"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.params = None
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        # Mock where FunctionBuilder is imported in the cli.main module
        with patch.object(cli_main, "FunctionBuilder") as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.validate.return_value = MagicMock(valid=True)

            result = handle_test_command(mock_args)

            assert result == 0
            mock_instance.validate.assert_called_once_with(
                python_file=str(valid_python_file),
                requirements_file=None,
                test_params=None,
            )

    def test_test_command_with_params(self, mock_args, valid_python_file):
        """Test command with parameters"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.params = '{"name": "World"}'
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "FunctionBuilder") as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.validate.return_value = MagicMock(valid=True)

            result = handle_test_command(mock_args)

        assert result == 0
        mock_instance.validate.assert_called_once_with(
            python_file=str(valid_python_file),
            requirements_file=None,
            test_params={"name": "World"},
        )

    def test_test_command_invalid_json_params(self, mock_args, valid_python_file):
        """Test command with invalid JSON parameters"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.params = "not valid json"
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        result = handle_test_command(mock_args)
        assert result == 1

    def test_test_command_validation_failure(self, mock_args, valid_python_file):
        """Test command when validation fails"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.params = None
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "FunctionBuilder") as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.validate.return_value = MagicMock(valid=False)

            result = handle_test_command(mock_args)

        assert result == 1

    def test_test_command_with_requirements(
        self, mock_args, valid_python_file, tmp_path
    ):
        """Test command with requirements file"""
        requirements_file = tmp_path / "requirements.txt"
        requirements_file.write_text("requests==2.28.0\nnumpy>=1.20.0")

        mock_args.file = str(valid_python_file)
        mock_args.requirements = str(requirements_file)
        mock_args.params = None
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "FunctionBuilder") as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.validate.return_value = MagicMock(valid=True)

            result = handle_test_command(mock_args)

        assert result == 0
        mock_instance.validate.assert_called_once_with(
            python_file=str(valid_python_file),
            requirements_file=str(requirements_file),
            test_params=None,
        )

    # ==================== Deploy Command Tests ====================

    def test_deploy_command_success(self, mock_args, valid_python_file, tmp_path):
        """Deploy command successful deployment"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180
        # Make sure server attribute doesn't exist for this test
        if hasattr(mock_args, "server"):
            delattr(mock_args, "server")

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch.object(cli_main, "CredentialManager") as mock_cred:
                mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
                mock_cred.return_value.get_credentials.return_value = (
                    "testuser",
                    "testpass",
                )

                with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                    mock_instance = mock_builder.return_value
                    mock_instance.validator.check_syntax.return_value = MagicMock(
                        valid=True,
                        info={"keynet_function_name": "test-function"},
                        errors=[],
                    )
                    mock_instance.deploy.return_value = True

                    result = deploy_command(mock_args)

                    assert result == 0
                    mock_instance.deploy.assert_called_once()

    def test_deploy_no_login(self, mock_args, valid_python_file):
        """Test deploy when not logged in"""
        mock_args.file = str(valid_python_file)

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = []
            result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_no_decorator_name(self, mock_args, valid_python_file):
        """Deploy command when decorator name is missing"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=True,
                    info={},
                    errors=[],  # No keynet_function_name
                )

                result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_validation_failure(self, mock_args, valid_python_file):
        """Test deploy when validation fails"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=False, errors=["Syntax error"], info={}
                )

                result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_config_value_error(self, mock_args, valid_python_file):
        """Test deploy with invalid config values"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "2.7"  # Invalid version
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=True, info={"keynet_function_name": "test-func"}, errors=[]
                )

                result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_failed_credential_retrieval(self, mock_args, valid_python_file):
        """Test deploy when credential retrieval fails"""
        mock_args.file = str(valid_python_file)

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = (
                None  # Failed to get credentials
            )

            result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_deployment_failure(self, mock_args, valid_python_file):
        """Test deploy when deployment fails"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=True, info={"keynet_function_name": "test-func"}, errors=[]
                )
                mock_instance.deploy.return_value = False  # Deployment fails

                result = deploy_command(mock_args)

        assert result == 1

    def test_deploy_with_server_specified(self, mock_args, valid_python_file):
        """Test deploy with specific server specified"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180
        mock_args.server = "staging.keynet.io"

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = [
                "api.keynet.io",
                "staging.keynet.io",
            ]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=True, info={"keynet_function_name": "test-func"}, errors=[]
                )
                mock_instance.deploy.return_value = True

                result = deploy_command(mock_args)

        assert result == 0
        # Should use the specified server
        mock_cred.return_value.get_credentials.assert_called_with("staging.keynet.io")

    def test_deploy_server_not_in_credentials(self, mock_args, valid_python_file):
        """Test deploy when specified server is not in credentials"""
        mock_args.file = str(valid_python_file)
        mock_args.server = "unknown.keynet.io"

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            result = deploy_command(mock_args)

        assert result == 1

    # ==================== Main Function Tests ====================

    def test_main_no_args(self):
        """Test main with no arguments"""
        with patch.object(sys, "argv", ["keynet"]):
            with patch("argparse.ArgumentParser.print_help") as mock_help:
                result = main()

        assert result == 1
        mock_help.assert_called_once()

    def test_main_login(self):
        """Test main with login command"""
        with patch.object(sys, "argv", ["keynet", "login", "api.keynet.io"]):
            with patch.object(cli_main, "login_command") as mock_login:
                mock_login.return_value = 0
                result = main()

        assert result == 0
        mock_login.assert_called_once()

    def test_main_logout(self):
        """Test main with logout command"""
        with patch.object(sys, "argv", ["keynet", "logout"]):
            with patch.object(cli_main, "logout_command") as mock_logout:
                mock_logout.return_value = 0
                result = main()

        assert result == 0
        mock_logout.assert_called_once()

    def test_main_logout_with_options(self):
        """Test main with logout command and options"""
        with patch.object(sys, "argv", ["keynet", "logout", "--all"]):
            with patch.object(cli_main, "logout_command") as mock_logout:
                mock_logout.return_value = 0
                result = main()

        assert result == 0
        mock_logout.assert_called_once()
        args = mock_logout.call_args[0][0]
        assert args.all is True

    def test_main_test(self):
        """Test main with test command"""
        with patch.object(sys, "argv", ["keynet", "test", "function.py"]):
            with patch.object(cli_main, "handle_test_command") as mock_test:
                mock_test.return_value = 0
                result = main()

        assert result == 0
        mock_test.assert_called_once()

    def test_main_test_with_params(self):
        """Test main with test command and parameters"""
        with patch.object(
            sys,
            "argv",
            ["keynet", "test", "function.py", "--params", '{"key": "value"}'],
        ):
            with patch.object(cli_main, "handle_test_command") as mock_test:
                mock_test.return_value = 0
                result = main()

        assert result == 0
        mock_test.assert_called_once()
        args = mock_test.call_args[0][0]
        assert args.params == '{"key": "value"}'

    def test_main_deploy(self):
        """Test main with deploy command"""
        with patch.object(sys, "argv", ["keynet", "deploy", "function.py"]):
            with patch.object(cli_main, "deploy_command") as mock_deploy:
                mock_deploy.return_value = 0
                result = main()

        assert result == 0
        mock_deploy.assert_called_once()

    def test_main_deploy_with_options(self):
        """Test main with deploy command and options"""
        with patch.object(
            sys,
            "argv",
            [
                "keynet",
                "deploy",
                "function.py",
                "--python-version",
                "3.11",
                "--memory",
                "512",
                "-r",
                "requirements.txt",
            ],
        ):
            with patch.object(cli_main, "deploy_command") as mock_deploy:
                mock_deploy.return_value = 0
                result = main()

        assert result == 0
        mock_deploy.assert_called_once()
        args = mock_deploy.call_args[0][0]
        assert args.python_version == "3.11"
        assert args.memory == 512
        assert args.requirements == "requirements.txt"

    def test_main_invalid_command(self):
        """Test main with invalid command"""
        with patch.object(sys, "argv", ["keynet", "invalid"]):
            with patch("argparse.ArgumentParser.print_help"):
                with patch("sys.stderr.write"):  # Suppress error output
                    with pytest.raises(SystemExit):
                        main()

    # ==================== Additional Edge Cases ====================

    def test_login_with_special_characters_in_password(self, mock_args):
        """Test login with special characters in password"""
        mock_args.server_domain = "api.keynet.io"
        special_password = "p@$$w0rd!#$%^&*()"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value=special_password):
                with patch.object(cli_main, "AuthClient") as mock_auth:
                    with patch.object(cli_main, "CredentialManager") as mock_cred:
                        mock_auth.return_value.authenticate.return_value = (
                            True,
                            "token",
                        )
                        result = login_command(mock_args)

                        # Verify password was saved correctly
                        mock_cred.return_value.save_credentials.assert_called_with(
                            "api.keynet.io", "testuser", special_password
                        )

                        assert result == 0

    def test_test_command_with_large_params(self, mock_args, valid_python_file):
        """Test command with large JSON parameters"""
        large_params = {"data": ["item"] * 1000, "nested": {"key": "value" * 100}}
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.params = json.dumps(large_params)  # Convert to JSON string
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "FunctionBuilder") as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.validate.return_value = MagicMock(valid=True)

            result = handle_test_command(mock_args)

        assert result == 0

    def test_deploy_with_minimum_memory(self, mock_args, valid_python_file):
        """Test deploy with minimum memory setting"""
        mock_args.file = str(valid_python_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 128  # Minimum memory
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        with patch.object(cli_main, "CredentialManager") as mock_cred:
            mock_cred.return_value.list_servers.return_value = ["api.keynet.io"]
            mock_cred.return_value.get_credentials.return_value = ("user", "pass")

            with patch.object(cli_main, "FunctionBuilder") as mock_builder:
                mock_instance = mock_builder.return_value
                mock_instance.validator.check_syntax.return_value = MagicMock(
                    valid=True, info={"keynet_function_name": "test-func"}, errors=[]
                )
                mock_instance.deploy.return_value = True

                result = deploy_command(mock_args)

        assert result == 0

    def test_concurrent_login_attempts(self, mock_args):
        """Test handling of concurrent login attempts"""
        mock_args.server_domain = "api.keynet.io"

        with patch("builtins.input", return_value="testuser"):
            with patch("getpass.getpass", return_value="testpass"):
                with patch.object(cli_main, "AuthClient") as mock_auth:
                    with patch.object(cli_main, "CredentialManager"):
                        # Simulate rate limiting or concurrent access error
                        mock_auth.return_value.authenticate.return_value = (
                            False,
                            "Too many requests",
                        )
                        result = login_command(mock_args)

                        assert result == 1
