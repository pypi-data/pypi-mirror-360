import re
from pathlib import Path
from typing import Any, Optional

from .models import FunctionConfig, ValidationResult
from .validator import FunctionValidator
from .venv_manager import VenvManager


class FunctionBuilder:
    """
    OpenWhisk 함수를 배포하기 위한 빌더

    main.py 로 사용한 파이썬 파일 한개와, 의존성 목록을 정의한 requirements.txt 파일을 받아서,
    해당 파일을 검증하고, 배포하는 기능을 제공합니다.

    Args:
        import_timeout: 파이썬 파일 임포트 시간 초과 시간
        execution_timeout: 파이썬 파일 실행 시간 초과 시간

    """

    # OpenWhisk 제한사항
    MAX_CODE_SIZE = 48 * 1024 * 1024  # 48MB

    # 보안 패턴
    DANGEROUS_PATTERNS = [
        (r"exec\s*\(", "exec() 사용 감지"),
        (r"eval\s*\(", "eval() 사용 감지"),
        (r"__import__\s*\(", "__import__() 사용 감지"),
        (r"compile\s*\(", "compile() 사용 감지"),
        (r"open\s*\(.*['\"](?:/etc/|/root/|/home/)", "시스템 파일 접근 시도"),
        (r"subprocess\.", "subprocess 모듈 사용 감지"),
        (r"os\.system\s*\(", "os.system() 사용 감지"),
    ]

    def __init__(self, import_timeout: int = 120, execution_timeout: int = 180):
        # 초기화
        cache_dir = Path.home() / ".wtu_function"
        self.venv_manager = VenvManager(cache_dir)
        self.validator = FunctionValidator(
            self.venv_manager, import_timeout, execution_timeout
        )

    def validate(
        self,
        python_file: str,
        requirements_file: Optional[str] = None,
        test_params: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """로컬 검증"""
        print("🔍 함수 검증 중...")

        result = self.validator.validate(python_file, requirements_file, test_params)

        self._print_validation_result(result)
        return result

    def deploy(
        self,
        config: FunctionConfig,
        validate_first: bool = True,
        test_params: Optional[dict[str, Any]] = None,
    ) -> bool:
        """함수 배포"""
        print(f"🚀 {config.name} 배포 시작...")

        # 검증
        if validate_first:
            validation = self.validate(
                config.python_file, config.requirements_file, test_params
            )
            if not validation.valid:
                print("❌ 검증 실패로 배포 중단")
                return False

        # 서버에 업로드
        success = self._upload_to_server(config)

        if success:
            print(f"✅ {config.name} 배포 완료!")
        else:
            print("❌ 배포 실패")

        return success

    def _validate_file(
        self, file_path: str, file_type: str = "python"
    ) -> ValidationResult:
        """파일 검증 (크기, 인코딩, 보안)"""
        result = ValidationResult()
        path = Path(file_path)

        # 파일 존재 확인
        if not path.exists():
            result.errors.append(f"파일이 존재하지 않습니다: {file_path}")
            result.valid = False
            return result

        # 파일 크기 검증
        file_size = path.stat().st_size
        if file_size > self.MAX_CODE_SIZE:
            result.errors.append(
                f"파일 크기가 제한을 초과합니다: {file_size / 1024 / 1024:.1f}MB (최대: 48MB)"
            )
            result.valid = False
            return result

        # UTF-8 인코딩 검증
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            result.errors.append("파일이 UTF-8로 인코딩되지 않았습니다")
            result.valid = False
            return result

        # Python 파일인 경우 보안 패턴 검사
        if file_type == "python":
            for pattern, description in self.DANGEROUS_PATTERNS:
                if re.search(pattern, content, re.MULTILINE):
                    result.warnings.append(f"보안 경고: {description}")

        result.valid = len(result.errors) == 0
        result.info["file_size"] = file_size
        result.info["line_count"] = len(content.splitlines())

        return result

    def _upload_to_server(self, config: FunctionConfig) -> bool:
        """서버에 파일 업로드"""
        # 파일 검증
        python_validation = self._validate_file(config.python_file, "python")
        if not python_validation.valid:
            print("❌ Python 파일 검증 실패:")
            for error in python_validation.errors:
                print(f"   - {error}")
            return False

        if python_validation.warnings:
            print("⚠️  보안 경고:")
            for warning in python_validation.warnings:
                print(f"   - {warning}")

        if config.requirements_file:
            req_validation = self._validate_file(
                config.requirements_file, "requirements"
            )
            if not req_validation.valid:
                print("❌ Requirements 파일 검증 실패:")
                for error in req_validation.errors:
                    print(f"   - {error}")
                return False

        # 파일 준비
        files = {}

        # Context managers로 파일 처리
        try:
            with Path(config.python_file).open("rb") as main_file:
                files["main_py"] = ("main.py", main_file.read(), "text/x-python")

            if config.requirements_file:
                with Path(config.requirements_file).open("rb") as req_file:
                    files["requirements_txt"] = (
                        "requirements.txt",
                        req_file.read(),
                        "text/plain",
                    )

            # TODO: 실제 서버 API 호출
            # data = {
            #     "function_name": config.name,
            #     "python_version": config.python_version.value,
            #     "memory": config.memory,
            #     "timeout": config.timeout,
            # }
            # response = requests.post(...)

            # Mock response
            return True
        except Exception:
            return False

    def _print_validation_result(self, result: ValidationResult):
        """검증 결과 출력"""
        print("\n📊 검증 결과:")
        print(f"   상태: {'✅ 통과' if result.valid else '❌ 실패'}")

        if result.info:
            if "main_line" in result.info:
                print(f"   main 함수: {result.info['main_line']}번째 줄")
            if "execution_time" in result.info:
                print(f"   실행 시간: {result.info['execution_time']:.3f}초")

        if result.warnings:
            print(f"\n⚠️  경고 ({len(result.warnings)}개):")
            for warning in result.warnings:
                print(f"   - {warning}")

        if result.errors:
            print(f"\n❌ 오류 ({len(result.errors)}개):")
            for error in result.errors:
                print(f"   - {error}")

        print()
