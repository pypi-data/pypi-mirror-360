import threading
import time

import pytest

from keynet_inference.function.decorator import (
    get_function_metadata,
    is_inside_keynet_function,
    keynet_function,
)
from keynet_inference.function.validator import FunctionValidator
from keynet_inference.function.venv_manager import VenvManager


class TestKeynetFunctionDecorator:
    """@keynet_function 데코레이터 테스트"""

    def test_decorator_basic_usage(self):
        """기본 사용법 테스트"""

        @keynet_function("test-function")
        def my_function(args):
            return args.get("x", 0) * 2

        # 메타데이터 확인
        metadata = get_function_metadata(my_function)
        assert metadata is not None
        assert metadata["name"] == "test-function"
        assert metadata["is_keynet_function"] is True

        # 함수가 정상 작동하는지 확인
        assert my_function({"x": 5}) == 10

    # Name validation tests moved to test_decorator_validation.py

    def test_context_tracking(self):
        """컨텍스트 추적 테스트"""

        @keynet_function("outer")
        def outer_function(args):
            assert is_inside_keynet_function() is True
            inner_function()
            return "outer"

        def inner_function():
            # outer가 keynet_function이면 inner도 컨텍스트 내부
            assert is_inside_keynet_function() is True

        # 함수 외부에서는 False
        assert is_inside_keynet_function() is False

        # 함수 실행
        result = outer_function({})
        assert result == "outer"

        # 함수 실행 후에도 False
        assert is_inside_keynet_function() is False

    def test_nested_decorators(self):
        """중첩된 데코레이터 사용"""

        @keynet_function("level1")
        def level1(args):
            assert is_inside_keynet_function() is True
            return level2({})

        @keynet_function("level2")
        def level2(args):
            assert is_inside_keynet_function() is True
            return "nested"

        result = level1({})
        assert result == "nested"

    def test_decorator_preserves_function_attributes(self):
        """functools.wraps가 제대로 작동하는지 확인"""

        @keynet_function("documented")
        def documented_function(args):
            """Documented function for testing attribute preservation."""
            return "doc"

        assert documented_function.__name__ == "documented_function"
        assert (
            documented_function.__doc__
            == "Documented function for testing attribute preservation."
        )

    def test_args_not_dict_error(self):
        """Test that TypeError is raised when args is not a dict"""

        @keynet_function("test-function")
        def main(args):
            return {"result": "success"}

        # Test with string instead of dict
        with pytest.raises(
            TypeError, match="Expected 'args' parameter to be a dict, got str"
        ):
            main("not a dict")

        # Test with list instead of dict
        with pytest.raises(
            TypeError, match="Expected 'args' parameter to be a dict, got list"
        ):
            main([1, 2, 3])

        # Test with None
        with pytest.raises(
            TypeError, match="Expected 'args' parameter to be a dict, got NoneType"
        ):
            main(None)

    def test_args_empty_dict(self):
        """Test with empty args dict"""

        @keynet_function("test-function")
        def main(args):
            return {"result": "success"}

        # Should work fine with empty dict
        result = main({})
        assert result == {"result": "success"}

    def test_exception_in_decorated_function(self):
        """Test that exceptions in decorated function are propagated"""

        @keynet_function("test-function")
        def main(args):
            raise RuntimeError("Function failed")

        with pytest.raises(RuntimeError, match="Function failed"):
            main({"test": "data"})

    def test_return_value_preservation(self):
        """Test that various return values are preserved correctly"""

        @keynet_function("test-function")
        def main(args):
            if args.get("return_none"):
                return None
            elif args.get("return_list"):
                return [1, 2, 3]
            elif args.get("return_string"):
                return "test string"
            else:
                return {"default": True}

        # Test None return
        assert main({"return_none": True}) is None

        # Test list return
        assert main({"return_list": True}) == [1, 2, 3]

        # Test string return
        assert main({"return_string": True}) == "test string"

        # Test dict return
        assert main({}) == {"default": True}

    def test_concurrent_execution(self):
        """Test thread safety of decorator"""
        results = []

        @keynet_function("concurrent-function")
        def main(args):
            # Simulate some work
            time.sleep(0.01)
            return {"thread_id": args["thread_id"]}

        def run_function(thread_id):
            result = main({"thread_id": thread_id})
            results.append(result)

        # Run multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=run_function, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Check all results are correct
        assert len(results) == 5
        thread_ids = sorted([r["thread_id"] for r in results])
        assert thread_ids == [0, 1, 2, 3, 4]


class TestValidatorWithDecorator:
    """데코레이터 검증이 포함된 Validator 테스트"""

    @pytest.fixture
    def validator(self, tmp_path):
        """Validator 인스턴스"""
        venv_manager = VenvManager(tmp_path)
        return FunctionValidator(venv_manager)

    def test_valid_decorated_main(self, validator, tmp_path):
        """올바르게 데코레이트된 main 함수"""
        python_file = tmp_path / "valid_decorated.py"
        python_file.write_text("""
from keynet_inference.function.decorator import keynet_function

@keynet_function("my-serverless-function")
def main(args):
    return {"message": "Hello World"}
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is True
        assert result.info["keynet_function_name"] == "my-serverless-function"

    def test_main_without_decorator(self, validator, tmp_path):
        """데코레이터 없는 main 함수"""
        python_file = tmp_path / "no_decorator.py"
        python_file.write_text("""
def main(args):
    return {"message": "Hello World"}
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is False
        assert any(
            "@keynet_function 데코레이터가 없습니다" in error for error in result.errors
        )

    def test_decorator_without_name(self, validator, tmp_path):
        """이름 없이 사용된 데코레이터"""
        python_file = tmp_path / "decorator_no_name.py"
        python_file.write_text("""
from keynet_inference.function.decorator import keynet_function

@keynet_function
def main(args):
    return {"message": "Hello World"}
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is False
        assert any("반드시 함수 이름을 인자로" in error for error in result.errors)

    def test_other_decorators_ignored(self, validator, tmp_path):
        """다른 데코레이터는 무시"""
        python_file = tmp_path / "other_decorator.py"
        python_file.write_text("""
from functools import cache

@cache
def main(args):
    return {"message": "Hello World"}
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is False
        assert any(
            "@keynet_function 데코레이터가 없습니다" in error for error in result.errors
        )

    def test_multiple_decorators(self, validator, tmp_path):
        """여러 데코레이터와 함께 사용"""
        python_file = tmp_path / "multiple_decorators.py"
        python_file.write_text("""
from functools import lru_cache
from keynet_inference.function.decorator import keynet_function

@lru_cache(maxsize=128)
@keynet_function("cached-function")
def main(args):
    return {"message": "Hello World"}
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is True
        assert result.info["keynet_function_name"] == "cached-function"

    def test_nested_function_calls(self, validator, tmp_path):
        """중첩된 함수 호출"""
        python_file = tmp_path / "nested_calls.py"
        python_file.write_text("""
from keynet_inference.function.decorator import keynet_function, is_inside_keynet_function

def helper_function():
    # main이 keynet_function으로 데코레이트되었으므로 True여야 함
    if is_inside_keynet_function():
        return {"nested": True}
    return {"nested": False}

@keynet_function("nested-example")
def main(args):
    return helper_function()
""")

        result = validator.check_syntax(str(python_file))
        assert result.valid is True
        assert result.info["keynet_function_name"] == "nested-example"
