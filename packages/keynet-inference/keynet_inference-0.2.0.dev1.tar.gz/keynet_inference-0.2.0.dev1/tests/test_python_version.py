import pytest

from keynet_inference.function.models import (
    FunctionConfig,
    PythonVersion,
)


class TestPythonVersion:
    """PythonVersion enum 테스트"""

    def test_enum_values(self):
        """열거형 값 확인"""
        assert PythonVersion.PYTHON_3_9.value == "3.9"
        assert PythonVersion.PYTHON_3_10.value == "3.10"
        assert PythonVersion.PYTHON_3_11.value == "3.11"
        assert PythonVersion.PYTHON_3_12.value == "3.12"

    def test_default_version(self):
        """기본 버전 확인"""
        assert PythonVersion.get_default() == PythonVersion.PYTHON_3_12

    def test_from_string_valid(self):
        """유효한 문자열 변환"""
        assert PythonVersion.from_string("3.9") == PythonVersion.PYTHON_3_9
        assert PythonVersion.from_string("3.10") == PythonVersion.PYTHON_3_10
        assert PythonVersion.from_string("3.11") == PythonVersion.PYTHON_3_11
        assert PythonVersion.from_string("3.12") == PythonVersion.PYTHON_3_12

    def test_from_string_invalid(self):
        """유효하지 않은 문자열 변환"""
        with pytest.raises(ValueError, match="Unsupported Python version: 3.8"):
            PythonVersion.from_string("3.8")

        with pytest.raises(ValueError, match="Unsupported Python version: 3.13"):
            PythonVersion.from_string("3.13")

        with pytest.raises(ValueError, match="Unsupported Python version: invalid"):
            PythonVersion.from_string("invalid")

    def test_function_config_with_enum(self, temp_dir):
        """FunctionConfig에서 enum 사용"""
        # 테스트 파일 생성
        test_file = temp_dir / "test.py"
        test_file.write_text("def main(args): pass")

        # enum으로 직접 설정
        config = FunctionConfig(
            name="test",
            python_file=str(test_file),
            python_version=PythonVersion.PYTHON_3_9,
        )
        assert config.python_version == PythonVersion.PYTHON_3_9

    def test_function_config_with_string(self, temp_dir):
        """FunctionConfig에서 문자열로 버전 전달"""
        # 테스트 파일 생성
        test_file = temp_dir / "test.py"
        test_file.write_text("def main(args): pass")

        # 문자열로 설정 (자동 변환)
        config = FunctionConfig(
            name="test", python_file=str(test_file), python_version="3.10"
        )
        assert config.python_version == PythonVersion.PYTHON_3_10

    def test_function_config_invalid_version(self, temp_dir):
        """FunctionConfig에서 유효하지 않은 버전"""
        # 테스트 파일 생성
        test_file = temp_dir / "test.py"
        test_file.write_text("def main(args): pass")

        # 유효하지 않은 버전
        with pytest.raises(ValueError, match="Unsupported Python version"):
            FunctionConfig(
                name="test", python_file=str(test_file), python_version="3.13"
            )

    def test_function_config_default_version(self, temp_dir):
        """FunctionConfig 기본 버전"""
        # 테스트 파일 생성
        test_file = temp_dir / "test.py"
        test_file.write_text("def main(args): pass")

        # 버전을 지정하지 않으면 기본값 사용
        config = FunctionConfig(name="test", python_file=str(test_file))
        assert config.python_version == PythonVersion.PYTHON_3_12

    def test_str_enum_behavior(self):
        """str을 상속한 enum의 동작 확인"""
        # str을 상속했으므로 문자열처럼 사용 가능
        version = PythonVersion.PYTHON_3_12
        assert version == "3.12"
        assert version.value == "3.12"
        assert f"Python {version.value}" == "Python 3.12"

    def test_all_versions_list(self):
        """모든 지원 버전 목록 확인"""
        supported_versions = [v.value for v in PythonVersion]
        expected = ["3.9", "3.10", "3.11", "3.12"]
        assert supported_versions == expected
