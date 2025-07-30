# models.py
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class PythonVersion(str, Enum):
    """지원하는 Python 버전"""

    PYTHON_3_9 = "3.9"
    PYTHON_3_10 = "3.10"
    PYTHON_3_11 = "3.11"
    PYTHON_3_12 = "3.12"

    @classmethod
    def get_default(cls) -> "PythonVersion":
        """기본 Python 버전"""
        return cls.PYTHON_3_12

    @classmethod
    def from_string(cls, version: str) -> "PythonVersion":
        """문자열에서 PythonVersion으로 변환"""
        for pv in cls:
            if pv.value == version:
                return pv
        raise ValueError(
            f"Unsupported Python version: {version}. Supported versions: {[v.value for v in cls]}"
        )


@dataclass
class FunctionConfig:
    """함수 설정"""

    name: str
    python_file: str
    requirements_file: Optional[str] = None
    python_version: PythonVersion = PythonVersion.PYTHON_3_12
    memory: int = 256
    timeout: int = 60

    def __post_init__(self):
        # Python 버전이 문자열로 전달된 경우 변환
        if isinstance(self.python_version, str):
            self.python_version = PythonVersion.from_string(self.python_version)

        # 1. 경로를 절대 경로로 변환 (상대 경로 문제 해결)
        self.python_file = str(Path(self.python_file).resolve())

        # 2. 경로 보안 검증 (다른 검사 전에 수행)
        if not self.is_safe_path(self.python_file):
            raise ValueError(f"Unsafe path: {self.python_file}")

        # 3. 파일 존재 확인
        if not Path(self.python_file).exists():
            raise FileNotFoundError(f"Python file not found: {self.python_file}")

        # 4. 파일인지 확인 (디렉토리가 아닌지)
        if not Path(self.python_file).is_file():
            raise ValueError(f"Not a file: {self.python_file}")

        # 5. 읽기 권한 확인
        if not os.access(self.python_file, os.R_OK):
            raise PermissionError(f"Cannot read file: {self.python_file}")

        # 6. 파일 확장자 확인
        if not self.python_file.endswith(".py"):
            raise ValueError(f"Not a Python file: {self.python_file}")

        # 7. 파일 크기 확인 (너무 큰 파일 방지)
        file_size = Path(self.python_file).stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB 제한
            raise ValueError(f"File too large: {file_size} bytes")

        # requirements 파일도 동일하게 처리
        if self.requirements_file:
            self.requirements_file = str(Path(self.requirements_file).resolve())

            if not Path(self.requirements_file).exists():
                raise FileNotFoundError(
                    f"Requirements file not found: {self.requirements_file}"
                )

            if not Path(self.requirements_file).is_file():
                raise ValueError(f"Not a file: {self.requirements_file}")

            if not os.access(self.requirements_file, os.R_OK):
                raise PermissionError(f"Cannot read file: {self.requirements_file}")

            # requirements.txt 또는 .txt 확장자 확인
            if not (
                self.requirements_file.endswith(".txt")
                or self.requirements_file.endswith("requirements.txt")
            ):
                raise ValueError(f"Invalid requirements file: {self.requirements_file}")

            # 경로 보안 검증
            if not self.is_safe_path(self.requirements_file):
                raise ValueError(f"Unsafe path: {self.requirements_file}")

    def is_safe_path(self, path: str) -> bool:
        """경로 순회 공격 방지"""
        import tempfile

        # 절대 경로로 변환 (심볼릭 링크 해결)
        abs_path = Path(path).resolve()

        # 안전한 경로 목록
        safe_paths = []

        # 현재 작업 디렉토리
        import contextlib

        with contextlib.suppress(FileNotFoundError):
            safe_paths.append(Path.cwd().resolve())

        # 홈 디렉토리
        safe_paths.append(Path.home().resolve())

        # 시스템 임시 디렉토리
        safe_paths.append(Path(tempfile.gettempdir()).resolve())

        # 안전한 경로 하위인지 확인
        for safe_path in safe_paths:
            try:
                abs_path.relative_to(safe_path)
                return True
            except ValueError:
                continue

        return False


@dataclass
class ValidationResult:
    """검증 결과"""

    valid: bool = True
    errors: Optional[list[str]] = None
    warnings: Optional[list[str]] = None
    info: Optional[dict[str, Any]] = None

    def __post_init__(self):
        self.errors = self.errors or []
        self.warnings = self.warnings or []
        self.info = self.info or {}
