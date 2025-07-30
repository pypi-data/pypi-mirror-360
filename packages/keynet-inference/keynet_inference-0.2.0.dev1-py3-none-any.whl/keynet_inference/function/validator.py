# validator.py
import ast
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

from .models import ValidationResult
from .venv_manager import VenvManager


class FunctionValidator:
    """함수 검증기"""

    def __init__(
        self,
        venv_manager: VenvManager,
        import_timeout: int = 30,
        execution_timeout: int = 60,
    ):
        self.venv_manager = venv_manager
        self.import_timeout = import_timeout
        self.execution_timeout = execution_timeout

    def validate(
        self,
        python_file: str,
        requirements_file: Optional[str] = None,
        test_params: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """함수 전체 검증"""
        result = ValidationResult()

        # 1. 문법 검사
        syntax_result = self.check_syntax(python_file)
        if not syntax_result.valid:
            return syntax_result

        result.info.update(syntax_result.info)

        # 2. 의존성이 있거나 테스트 파라미터가 있는 경우 venv에서 검증
        if requirements_file or test_params is not None:
            venv_path, cached = self.venv_manager.get_or_create(requirements_file)
            result.info["venv_cached"] = cached

            # import 테스트
            import_result = self.test_import(venv_path, python_file)
            if not import_result.valid:
                return import_result

            # 실행 테스트 (test_params가 명시적으로 제공된 경우)
            if test_params is not None:
                exec_result = self.test_execution(venv_path, python_file, test_params)
                if not exec_result.valid:
                    return exec_result
                result.info.update(exec_result.info)

        return result

    def check_syntax(self, python_file: str) -> ValidationResult:
        """Python 문법 및 구조 검사"""
        result = ValidationResult()

        try:
            with Path(python_file).open() as f:
                code = f.read()

            # AST 파싱
            tree = ast.parse(code)

            # main 함수 찾기 및 데코레이터 검증
            main_found = False
            has_keynet_decorator = False

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "main":
                    main_found = True
                    result.info["main_line"] = node.lineno
                    result.info["main_args"] = [arg.arg for arg in node.args.args]

                    # Check main function signature
                    if len(node.args.args) != 1 or node.args.args[0].arg != "args":
                        result.valid = False
                        result.errors.append(
                            f"main 함수는 정확히 하나의 'args' 매개변수를 가져야 합니다. "
                            f"현재: {[arg.arg for arg in node.args.args]}"
                        )
                        return result

                    # 데코레이터 검사
                    for decorator in node.decorator_list:
                        # @keynet_function("name") 형태 검사
                        if isinstance(decorator, ast.Call):
                            if (
                                isinstance(decorator.func, ast.Name)
                                and decorator.func.id == "keynet_function"
                            ):
                                has_keynet_decorator = True
                                # 인자 검사
                                if len(decorator.args) > 0 and isinstance(
                                    decorator.args[0], ast.Constant
                                ):
                                    result.info["keynet_function_name"] = (
                                        decorator.args[0].value
                                    )
                        # @keynet_function 형태 (인자 없음) - 오류
                        elif (
                            isinstance(decorator, ast.Name)
                            and decorator.id == "keynet_function"
                        ):
                            result.valid = False
                            result.errors.append(
                                "@keynet_function 데코레이터는 반드시 함수 이름을 인자로 받아야 합니다"
                            )
                            return result
                    break

            if not main_found:
                result.valid = False
                result.errors.append("main 함수를 찾을 수 없습니다")
            elif not has_keynet_decorator:
                result.valid = False
                result.errors.append(
                    "main 함수에 @keynet_function 데코레이터가 없습니다"
                )
            else:
                result.info["has_main_function"] = True
                result.info["has_keynet_decorator"] = True

        except SyntaxError as e:
            result.valid = False
            result.errors.append(f"문법 오류: {e}")
        except Exception as e:
            result.valid = False
            result.errors.append(f"파일 읽기 오류: {e}")

        return result

    def test_import(self, venv_path: Path, python_file: str) -> ValidationResult:
        """Import 테스트"""
        result = ValidationResult()

        # 테스트 환경에서는 현재 Python 인터프리터 사용
        import sys

        if not venv_path.exists() or os.environ.get("PYTEST_CURRENT_TEST"):
            python_path = Path(sys.executable)
        else:
            python_path = self.venv_manager.get_python_path(venv_path)

        # 파일 경로를 안전하게 전달
        script = """import sys
import importlib.util
try:
    import resource
    # 메모리 제한: 512MB (Linux/macOS에서만 작동)
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
except:
    pass  # Windows나 resource 모듈이 없는 환경에서는 무시

python_file = sys.argv[1]
spec = importlib.util.spec_from_file_location("__main__", python_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print("SUCCESS")"""

        try:
            # 현재 프로세스의 환경 변수를 복사하고 PYTHONPATH 추가
            env = os.environ.copy()

            # 현재 패키지의 경로를 PYTHONPATH에 추가
            package_root = Path(
                __file__
            ).parent.parent.parent  # packages/inference 경로
            monorepo_root = package_root.parent  # 모노레포 루트

            # 기존 PYTHONPATH가 있으면 유지하면서 추가
            python_paths = [str(package_root), str(monorepo_root)]
            if "PYTHONPATH" in env:
                python_paths.insert(0, env["PYTHONPATH"])

            env["PYTHONPATH"] = os.pathsep.join(python_paths)

            proc = subprocess.run(
                [str(python_path), "-c", script, python_file],
                capture_output=True,
                text=True,
                timeout=self.import_timeout,
                env=env,
            )

            if proc.returncode != 0 or "SUCCESS" not in proc.stdout:
                result.valid = False
                result.errors.append(f"Import 실패: {proc.stderr}")

        except subprocess.TimeoutExpired:
            result.valid = False
            result.errors.append(f"Import 테스트 시간 초과 ({self.import_timeout}초)")

        return result

    def test_execution(
        self, venv_path: Path, python_file: str, test_params: dict[str, Any]
    ) -> ValidationResult:
        """함수 실행 테스트"""
        result = ValidationResult()

        # 테스트 환경에서는 현재 Python 인터프리터 사용
        import sys

        if not venv_path.exists() or os.environ.get("PYTEST_CURRENT_TEST"):
            python_path = Path(sys.executable)
        else:
            python_path = self.venv_manager.get_python_path(venv_path)

        script = """
import sys
import json
import time
import importlib.util

try:
    import resource
    # 메모리 제한: 512MB (Linux/macOS에서만 작동)
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
except:
    pass  # Windows나 resource 모듈이 없는 환경에서는 무시

python_file = sys.argv[1]
test_params = json.loads(sys.argv[2])

spec = importlib.util.spec_from_file_location("__main__", python_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

start = time.time()
try:
    output = module.main(test_params)
    elapsed = time.time() - start
    print(json.dumps({
        "success": True,
        "result": output,
        "time": elapsed
    }))
except MemoryError:
    print(json.dumps({
        "success": False,
        "error": "Memory limit exceeded"
    }))
except Exception as e:
    # 민감한 정보를 필터링
    error_msg = str(e)
    # 패스워드, API 키 등 민감한 패턴 제거
    import re
    error_msg = re.sub(r'(password|pass|pwd|secret|key|token)[\\s=:]*\\S+', '[REDACTED]', error_msg, flags=re.IGNORECASE)
    print(json.dumps({
        "success": False,
        "error": error_msg
    }))""".strip()

        try:
            # 현재 프로세스의 환경 변수를 복사하고 PYTHONPATH 추가
            env = os.environ.copy()

            # 현재 패키지의 경로를 PYTHONPATH에 추가
            package_root = Path(
                __file__
            ).parent.parent.parent  # packages/inference 경로
            monorepo_root = package_root.parent  # 모노레포 루트

            # 기존 PYTHONPATH가 있으면 유지하면서 추가
            python_paths = [str(package_root), str(monorepo_root)]
            if "PYTHONPATH" in env:
                python_paths.insert(0, env["PYTHONPATH"])

            env["PYTHONPATH"] = os.pathsep.join(python_paths)

            proc = subprocess.run(
                [str(python_path), "-c", script, python_file, json.dumps(test_params)],
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
                env=env,
            )

            try:
                output = json.loads(proc.stdout)
                if not output["success"]:
                    result.valid = False
                    result.errors.append(f"실행 실패: {output['error']}")
                else:
                    result.info["execution_time"] = output["time"]
                    result.info["test_result"] = output["result"]
            except Exception:
                result.valid = False
                result.errors.append(f"실행 오류: {proc.stderr}")

        except subprocess.TimeoutExpired:
            result.valid = False
            result.errors.append(f"함수 실행 시간 초과 ({self.execution_timeout}초)")

        return result
