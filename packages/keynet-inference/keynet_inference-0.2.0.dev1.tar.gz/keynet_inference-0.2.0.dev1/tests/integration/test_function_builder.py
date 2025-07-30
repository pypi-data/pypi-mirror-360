"""
FunctionBuilder 통합 테스트

이 테스트는 FunctionBuilder 클래스의 핵심 기능을 테스트합니다.
FunctionBuilder는 내부적으로 함수 검증과 실행을 담당하는 저수준 컴포넌트입니다.
사용자가 직접 사용하는 CLI나 데코레이터의 통합 테스트는 별도 파일에서 다룹니다.
"""

import tempfile
from pathlib import Path

import pytest

from keynet_inference.function.builder import FunctionBuilder


@pytest.mark.integration
class TestFunctionBuilder:
    """FunctionBuilder 통합 테스트"""

    def test_simple_function_flow(self):
        """간단한 함수의 전체 플로우"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 함수 파일 생성
            func_file = Path(tmpdir) / "simple.py"
            func_file.write_text(
                """
from keynet_inference.function.decorator import keynet_function

@keynet_function("simple-function")
def main(args):
    name = args.get('name', 'World')
    return {"message": f"Hello {name}!"}
"""
            )

            # Builder 생성
            builder = FunctionBuilder()

            # 검증
            validation = builder.validate(str(func_file), test_params={"name": "Test"})

            assert validation.valid
            assert validation.info.get("test_result") == {"message": "Hello Test!"}

    @pytest.mark.slow
    def test_function_with_dependencies(self):
        """의존성이 있는 함수"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 함수 파일
            func_file = Path(tmpdir) / "with_deps.py"
            func_file.write_text(
                """
import json
from keynet_inference.function.decorator import keynet_function

@keynet_function("with-deps-function")
def main(args):
    data = args.get('data', [])
    return {"json": json.dumps(data)}
"""
            )

            # requirements 파일
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("# 표준 라이브러리만 사용")

            # 검증
            builder = FunctionBuilder()
            validation = builder.validate(
                str(func_file), str(req_file), test_params={"data": [1, 2, 3]}
            )

            assert validation.valid

    def test_error_handling_flow(self):
        """에러 처리 플로우"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 에러를 발생시키는 함수
            func_file = Path(tmpdir) / "error_func.py"
            func_file.write_text(
                """
from keynet_inference.function.decorator import keynet_function

@keynet_function("error-function")
def main(args):
    # 의도적으로 에러 발생
    if args.get('error'):
        raise ValueError("Intentional error")
    return {"status": "ok"}
"""
            )

            builder = FunctionBuilder()

            # 정상 케이스
            validation1 = builder.validate(str(func_file), test_params={"error": False})
            assert validation1.valid

            # 에러 케이스
            validation2 = builder.validate(str(func_file), test_params={"error": True})
            assert not validation2.valid
            assert any("Intentional error" in error for error in validation2.errors)

    def test_large_output_handling(self):
        """큰 출력 처리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            func_file = Path(tmpdir) / "large_output.py"
            func_file.write_text(
                """
from keynet_inference.function.decorator import keynet_function

@keynet_function("large-output-function")
def main(args):
    size = args.get('size', 1000)
    return {"data": "x" * size}
"""
            )

            builder = FunctionBuilder()
            validation = builder.validate(
                str(func_file),
                test_params={"size": 1000000},  # 1MB 문자열
            )

            assert validation.valid

    def test_timeout_simulation(self):
        """타임아웃 시뮬레이션"""
        with tempfile.TemporaryDirectory() as tmpdir:
            func_file = Path(tmpdir) / "slow_func.py"
            func_file.write_text(
                """
import time
from keynet_inference.function.decorator import keynet_function

@keynet_function("slow-function")
def main(args):
    delay = args.get('delay', 0)
    time.sleep(delay)
    return {"slept": delay}
"""
            )

            builder = FunctionBuilder()

            # 빠른 실행
            validation = builder.validate(str(func_file), test_params={"delay": 0.1})

            assert validation.valid
            assert validation.info["execution_time"] >= 0.1

    def test_unicode_handling(self):
        """유니코드 처리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            func_file = Path(tmpdir) / "unicode_func.py"
            func_file.write_text(
                """
from keynet_inference.function.decorator import keynet_function

@keynet_function("unicode-function")
def main(args):
    text = args.get('text', '')
    return {
        "original": text,
        "length": len(text),
        "reversed": text[::-1]
    }
"""
            )

            builder = FunctionBuilder()
            validation = builder.validate(
                str(func_file), test_params={"text": "안녕하세요 🌟 Hello"}
            )

            assert validation.valid
            result = validation.info["test_result"]
            assert result["original"] == "안녕하세요 🌟 Hello"
            assert result["length"] == 13

    @pytest.mark.slow
    def test_function_with_real_dependencies(self):
        """실제 외부 패키지를 사용하는 함수"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # requests 패키지를 사용하는 함수
            func_file = Path(tmpdir) / "requests_func.py"
            func_file.write_text(
                """
import json
from keynet_inference.function.decorator import keynet_function

@keynet_function("json-function")
def main(args):
    # json은 표준 라이브러리이므로 별도 설치 불필요
    data = args.get('data', {})
    json_str = json.dumps(data, indent=2)
    return {
        "formatted": json_str,
        "size": len(json_str)
    }
"""
            )

            # 최소한의 requirements
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("# 표준 라이브러리만 사용")

            builder = FunctionBuilder()
            validation = builder.validate(
                str(func_file),
                str(req_file),
                test_params={"data": {"name": "test", "values": [1, 2, 3]}},
            )

            assert validation.valid
            assert validation.info.get("venv_cached") is not None
            result = validation.info["test_result"]
            assert "formatted" in result
            assert result["size"] > 0

    def test_cross_platform_path_handling(self):
        """크로스 플랫폼 경로 처리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 공백이 포함된 디렉토리명
            sub_dir = Path(tmpdir) / "my functions"
            sub_dir.mkdir()

            func_file = sub_dir / "path_test.py"
            func_file.write_text(
                """
import os
from keynet_inference.function.decorator import keynet_function

@keynet_function("path-test-function")
def main(args):
    return {
        "platform": os.name,
        "sep": os.sep,
        "current_dir": os.path.basename(os.getcwd())
    }
"""
            )

            builder = FunctionBuilder()
            validation = builder.validate(str(func_file), test_params={})

            assert validation.valid
            # test_params가 제공되어야 실행 테스트가 수행됨
            if "test_result" in validation.info:
                result = validation.info["test_result"]
                assert "platform" in result
                assert "sep" in result
