import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """임시 디렉토리 생성"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def fixtures_dir() -> Path:
    """테스트 fixtures 디렉토리"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_python_file(temp_dir: Path) -> Path:
    """유효한 Python 파일 생성"""
    file_path = temp_dir / "valid_function.py"
    file_path.write_text(
        """
# 테스트용 더미 데코레이터
def keynet_function(name):
    def decorator(func):
        return func
    return decorator

@keynet_function("test-function")
def main(args):
    name = args.get('name', 'World')
    return {"greeting": f"Hello {name}!"}
"""
    )
    return file_path


@pytest.fixture
def invalid_python_file(temp_dir: Path) -> Path:
    """문법 오류가 있는 Python 파일"""
    file_path = temp_dir / "invalid_syntax.py"
    file_path.write_text(
        """
def main(args:
    return {"error": "syntax error"}
"""
    )
    return file_path


@pytest.fixture
def no_main_python_file(temp_dir: Path) -> Path:
    """Main 함수가 없는 Python 파일"""
    file_path = temp_dir / "no_main.py"
    file_path.write_text(
        """
def hello():
    return "Hello"
"""
    )
    return file_path


@pytest.fixture
def requirements_file(temp_dir: Path) -> Path:
    """테스트용 requirements.txt"""
    file_path = temp_dir / "requirements.txt"
    file_path.write_text(
        """
requests==2.31.0
pytest==7.4.4
"""
    )
    return file_path


@pytest.fixture
def large_python_file(temp_dir: Path) -> Path:
    """10MB 이상의 큰 파일"""
    file_path = temp_dir / "large_file.py"
    # 11MB 파일 생성
    content = (
        "def keynet_function(name):\n    def decorator(func):\n        return func\n    return decorator\n\n# "
        + "x" * (11 * 1024 * 1024)
        + "\n@keynet_function('large')\ndef main(args): pass"
    )
    file_path.write_text(content)
    return file_path
