from unittest.mock import patch

import pytest

from keynet_inference.function.decorator import keynet_function


class TestDecoratorValidation:
    """Test @keynet_function decorator signature validation"""

    def test_valid_main_function(self):
        """Valid main function with single args parameter"""

        @keynet_function("test-function")
        def main(args):
            return {"result": "success"}

        # Should not raise any exception
        result = main({"test": "data"})
        assert result == {"result": "success"}

    def test_invalid_no_parameters(self):
        """Main function with no parameters should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main():
                return {"result": "success"}

    def test_invalid_wrong_parameter_name(self):
        """Main function with wrong parameter name should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(params):
                return {"result": "success"}

    def test_invalid_multiple_parameters(self):
        """Main function with multiple parameters should fail"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, extra):
                return {"result": "success"}

    def test_function_with_kwargs(self):
        """Test that function with kwargs raises error"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, **kwargs):
                return {}

    def test_function_with_defaults(self):
        """Test that function with default args raises error"""
        with pytest.raises(
            ValueError, match="must have exactly one parameter named 'args'"
        ):

            @keynet_function("test-function")
            def main(args, optional=None):
                return {}

    def test_decorator_with_empty_name(self):
        """Test decorator with empty name string"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function("")
            def main(args):
                return {}

    def test_decorator_with_whitespace_name(self):
        """Test decorator with whitespace-only name"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function("   ")
            def main(args):
                return {}

    def test_decorator_with_non_string_name(self):
        """Test decorator with non-string name"""
        with pytest.raises(
            ValueError, match="Function name must be a non-empty string"
        ):

            @keynet_function(123)  # type: ignore
            def main(args):
                return {}

    def test_openwhisk_runtime_flag(self):
        """Test OpenWhisk runtime flag detection"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # Test without runtime flag
        result = main({"param": "value"})
        assert result == {"input": {"param": "value"}}

        # Test with runtime flag
        with patch("keynet_inference.config.load_env") as mock_load_env:
            args_with_runtime = {"__ow_runtime": True, "param": "value"}
            result = main(args_with_runtime)

            # load_env should be called with the args
            mock_load_env.assert_called_once_with(args_with_runtime)
            assert result == {"input": args_with_runtime}

    def test_non_openwhisk_runtime(self):
        """Test that load_env is not called without runtime flag"""
        from unittest.mock import patch

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        with patch("keynet_inference.config.load_env") as mock_load_env:
            # Without __ow_runtime flag
            result = main({"param": "value"})

            # load_env should NOT be called
            mock_load_env.assert_not_called()
            assert result == {"input": {"param": "value"}}

            # With __ow_runtime = False
            result = main({"__ow_runtime": False, "param": "value"})

            # load_env should NOT be called
            mock_load_env.assert_not_called()

    def test_load_env_import_error_handling(self):
        """Test handling of load_env import errors"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # Mock the module import to raise error
        import sys

        original_modules = sys.modules.copy()
        sys.modules["keynet_inference.config"] = None

        try:
            # Should raise import error when trying to import
            with pytest.raises((ImportError, AttributeError)):
                main({"__ow_runtime": True, "param": "value"})
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_load_env_execution_error(self):
        """Test handling of load_env execution errors"""

        @keynet_function("test-function")
        def main(args):
            return {"input": args}

        # Mock load_env to raise an exception
        with patch(
            "keynet_inference.config.load_env",
            side_effect=Exception("Load env failed"),
        ):
            # Should propagate the exception
            with pytest.raises(Exception, match="Load env failed"):
                main({"__ow_runtime": True, "param": "value"})
