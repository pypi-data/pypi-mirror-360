"""
@keynet_function 데코레이터 통합 테스트

데코레이터의 전체 동작 플로우를 테스트합니다.
실제 함수 실행과 컨텍스트 관리를 포함합니다.
"""

import os
import threading
from unittest.mock import patch

import pytest

from keynet_inference.function.decorator import (
    get_function_metadata,
    is_inside_keynet_function,
    keynet_function,
)
from keynet_inference.function.validator import FunctionValidator
from keynet_inference.function.venv_manager import VenvManager


@pytest.mark.integration
class TestDecoratorIntegration:
    """@keynet_function 데코레이터 통합 테스트"""

    def test_decorator_with_validator_flow(self, tmp_path):
        """데코레이터와 Validator의 통합 플로우"""
        # 데코레이터를 사용한 함수 파일 생성
        func_file = tmp_path / "decorated_function.py"
        func_file.write_text("""
from keynet_inference.function.decorator import keynet_function

@keynet_function("my-serverless-function")
def main(args):
    name = args.get('name', 'World')
    return {"message": f"Hello {name}!", "decorated": True}
""")

        # Validator로 검증
        venv_manager = VenvManager(tmp_path / "venvs")
        validator = FunctionValidator(venv_manager)

        result = validator.check_syntax(str(func_file))
        assert result.valid
        assert result.info["keynet_function_name"] == "my-serverless-function"
        assert result.info["has_main_function"]
        assert result.info["has_keynet_decorator"]

    def test_nested_function_context_flow(self):
        """중첩된 함수 컨텍스트 플로우"""
        execution_log = []

        @keynet_function("outer-function")
        def outer_function(args):
            execution_log.append(("outer", is_inside_keynet_function()))
            result = helper_function()
            inner_function(args)
            return result

        def helper_function():
            execution_log.append(("helper", is_inside_keynet_function()))
            return {"helper": "called"}

        @keynet_function("inner-function")
        def inner_function(args):
            execution_log.append(("inner", is_inside_keynet_function()))
            return {"inner": "called"}

        # 함수 외부에서는 False
        assert not is_inside_keynet_function()

        # 함수 실행
        result = outer_function({"test": True})

        # 실행 로그 확인
        assert execution_log == [
            ("outer", True),  # outer 함수 내부
            ("helper", True),  # outer에서 호출된 helper
            ("inner", True),  # inner도 keynet_function이므로 True
        ]

        # 함수 실행 후에도 False
        assert not is_inside_keynet_function()

    def test_decorator_with_openwhisk_runtime(self):
        """OpenWhisk 런타임 환경 시뮬레이션"""

        @keynet_function("runtime-test-function")
        def main(args):
            return {
                "env_loaded": os.environ.get("KEYNET_ENV_LOADED", "false"),
                "runtime": args.get("__ow_runtime", False),
            }

        # 일반 실행
        result = main({"param": "value"})
        assert result["runtime"] is False

        # OpenWhisk 런타임 시뮬레이션
        with patch("keynet_inference.config.load_env") as mock_load_env:
            # load_env가 환경변수를 설정한다고 가정
            def set_env(args):
                os.environ["KEYNET_ENV_LOADED"] = "true"

            mock_load_env.side_effect = set_env

            result = main({"__ow_runtime": True, "param": "value"})

            # load_env가 호출되었는지 확인
            mock_load_env.assert_called_once()
            assert result["runtime"] is True

            # 환경변수 정리
            os.environ.pop("KEYNET_ENV_LOADED", None)

    def test_concurrent_decorated_functions(self):
        """동시 실행되는 데코레이터 함수들"""
        results = []
        errors = []

        @keynet_function("concurrent-func-1")
        def func1(args):
            import time

            time.sleep(0.01)  # 작은 지연
            return {"func": "1", "thread": threading.current_thread().name}

        @keynet_function("concurrent-func-2")
        def func2(args):
            import time

            time.sleep(0.01)  # 작은 지연
            return {"func": "2", "thread": threading.current_thread().name}

        def run_func(func, args, index):
            try:
                result = func(args)
                results.append((index, result))
            except Exception as e:
                errors.append((index, str(e)))

        # 여러 스레드에서 동시 실행
        threads = []
        for i in range(10):
            func = func1 if i % 2 == 0 else func2
            t = threading.Thread(target=run_func, args=(func, {"index": i}, i))
            threads.append(t)
            t.start()

        # 모든 스레드 완료 대기
        for t in threads:
            t.join()

        # 에러 없이 모두 완료되어야 함
        assert len(errors) == 0
        assert len(results) == 10

        # 각 함수가 올바른 결과 반환
        for index, result in results:
            expected_func = "1" if index % 2 == 0 else "2"
            assert result["func"] == expected_func

    def test_decorator_metadata_persistence(self):
        """데코레이터 메타데이터 지속성"""

        @keynet_function("metadata-test")
        def my_function(args):
            """Test function for metadata testing."""
            return {"test": True}

        # 메타데이터 확인
        metadata = get_function_metadata(my_function)
        assert metadata is not None
        assert metadata["name"] == "metadata-test"
        assert metadata["is_keynet_function"] is True

        # 함수 속성 보존
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "Test function for metadata testing."

        # 여러 번 호출해도 메타데이터 유지
        for _ in range(5):
            result = my_function({"iteration": _})
            assert result == {"test": True}

            # 메타데이터 재확인
            metadata = get_function_metadata(my_function)
            assert metadata["name"] == "metadata-test"

    def test_full_deployment_simulation(self, tmp_path):
        """전체 배포 시뮬레이션"""
        # 1. 함수 파일 생성
        func_file = tmp_path / "deploy_ready.py"
        func_file.write_text("""
from keynet_inference.function.decorator import keynet_function
import json
import os

@keynet_function("production-function")
def main(args):
    # 실제 비즈니스 로직
    action = args.get('action', 'default')

    if action == 'process':
        data = args.get('data', [])
        return {
            "processed": len(data),
            "summary": f"Processed {len(data)} items"
        }
    elif action == 'status':
        return {
            "status": "healthy",
            "version": "1.0.0",
            "python": os.sys.version.split()[0]
        }
    else:
        return {"message": "Ready for production"}
""")

        # 2. requirements 파일
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("# Production dependencies")

        # 3. Validator로 검증
        venv_manager = VenvManager(tmp_path / "venvs")
        validator = FunctionValidator(venv_manager)

        # 문법 검사
        syntax_result = validator.check_syntax(str(func_file))
        assert syntax_result.valid
        assert syntax_result.info["keynet_function_name"] == "production-function"

        # 4. 다양한 시나리오 테스트
        from keynet_inference.function.builder import FunctionBuilder

        builder = FunctionBuilder()

        # 기본 동작 테스트
        validation = builder.validate(str(func_file), str(req_file), test_params={})
        assert validation.valid
        assert validation.info["test_result"]["message"] == "Ready for production"

        # 프로세싱 테스트
        validation = builder.validate(
            str(func_file),
            str(req_file),
            test_params={"action": "process", "data": [1, 2, 3, 4, 5]},
        )
        assert validation.valid
        assert validation.info["test_result"]["processed"] == 5

        # 상태 확인 테스트
        validation = builder.validate(
            str(func_file), str(req_file), test_params={"action": "status"}
        )
        assert validation.valid
        assert validation.info["test_result"]["status"] == "healthy"

    def test_error_propagation_in_decorated_functions(self):
        """데코레이터 함수의 에러 전파"""

        @keynet_function("error-test-function")
        def main(args):
            error_type = args.get("error_type", "none")

            if error_type == "value":
                raise ValueError("Custom value error")
            elif error_type == "runtime":
                raise RuntimeError("Custom runtime error")
            elif error_type == "zero_division":
                return 1 / 0

            return {"status": "ok"}

        # 정상 실행
        result = main({"error_type": "none"})
        assert result["status"] == "ok"

        # ValueError 전파
        with pytest.raises(ValueError, match="Custom value error"):
            main({"error_type": "value"})

        # RuntimeError 전파
        with pytest.raises(RuntimeError, match="Custom runtime error"):
            main({"error_type": "runtime"})

        # ZeroDivisionError 전파
        with pytest.raises(ZeroDivisionError):
            main({"error_type": "zero_division"})
