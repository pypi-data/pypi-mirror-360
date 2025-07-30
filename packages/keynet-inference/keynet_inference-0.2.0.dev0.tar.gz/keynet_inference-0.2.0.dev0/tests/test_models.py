import os
from pathlib import Path

import pytest

from keynet_inference.function.models import (
    FunctionConfig,
    ValidationResult,
)


class TestFunctionConfig:
    """FunctionConfig 테스트"""

    def test_valid_config(self, valid_python_file):
        """유효한 설정 테스트"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )
        assert config.name == "test_function"
        assert Path(config.python_file).exists()
        assert config.python_version == "3.12"
        assert config.memory == 256
        assert config.timeout == 60

    def test_nonexistent_file(self):
        """존재하지 않는 파일"""
        # /nonexistent는 안전하지 않은 경로이므로 ValueError가 발생
        with pytest.raises(ValueError, match="Unsafe path"):
            FunctionConfig(name="test", python_file="/nonexistent/file.py")

    def test_directory_instead_of_file(self, temp_dir):
        """파일 대신 디렉토리"""
        with pytest.raises(ValueError, match="Not a file"):
            FunctionConfig(name="test", python_file=str(temp_dir))

    def test_non_python_file(self, temp_dir):
        """Python이 아닌 파일"""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Not a Python file")

        with pytest.raises(ValueError, match="Not a Python file"):
            FunctionConfig(name="test", python_file=str(txt_file))

    def test_large_file(self, large_python_file):
        """너무 큰 파일"""
        with pytest.raises(ValueError, match="File too large"):
            FunctionConfig(name="test", python_file=str(large_python_file))

    def test_no_read_permission(self, temp_dir):
        """읽기 권한이 없는 파일"""
        file_path = temp_dir / "no_read.py"
        file_path.write_text("def main(args): pass")
        file_path.chmod(0o000)

        try:
            with pytest.raises(PermissionError, match="Cannot read file"):
                FunctionConfig(name="test", python_file=str(file_path))
        finally:
            # 정리를 위해 권한 복구
            file_path.chmod(0o644)

    def test_relative_path_conversion(self, temp_dir):
        """상대 경로가 절대 경로로 변환되는지"""
        os.chdir(temp_dir)
        file_path = temp_dir / "test.py"
        file_path.write_text("def main(args): pass")

        config = FunctionConfig(name="test", python_file="./test.py")  # 상대 경로

        assert Path(config.python_file).is_absolute()
        assert Path(config.python_file).exists()

    def test_requirements_validation(self, valid_python_file, temp_dir):
        """Requirements 파일 검증"""
        # 유효한 requirements
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("requests==2.31.0")

        config = FunctionConfig(
            name="test",
            python_file=str(valid_python_file),
            requirements_file=str(req_file),
        )
        assert config.requirements_file == str(req_file.resolve())

        # 잘못된 확장자
        bad_req = temp_dir / "requirements.md"
        bad_req.write_text("# Requirements")

        with pytest.raises(ValueError, match="Invalid requirements file"):
            FunctionConfig(
                name="test",
                python_file=str(valid_python_file),
                requirements_file=str(bad_req),
            )

    def test_is_safe_path(self, valid_python_file):
        """안전한 경로 검증"""
        config = FunctionConfig(name="test", python_file=str(valid_python_file))

        # 현재 디렉토리 하위는 안전
        assert config.is_safe_path(str(valid_python_file))

        # 시스템 경로는 안전하지 않음
        assert not config.is_safe_path("/etc/passwd")

    def test_path_with_special_characters(self, temp_dir):
        """특수 문자가 포함된 경로"""
        # 공백이 포함된 파일명
        file_path = temp_dir / "my function.py"
        file_path.write_text("def main(args): pass")

        config = FunctionConfig(name="test", python_file=str(file_path))
        assert Path(config.python_file).exists()

    @pytest.mark.skipif(os.name == "nt", reason="심볼릭 링크는 Unix 계열에서만 테스트")
    def test_symlink_handling(self, temp_dir, valid_python_file):
        """심볼릭 링크 처리"""
        symlink_path = temp_dir / "link_to_function.py"
        symlink_path.symlink_to(valid_python_file)

        config = FunctionConfig(name="test", python_file=str(symlink_path))
        # resolve()로 실제 경로가 저장됨
        assert config.python_file == str(valid_python_file.resolve())


class TestValidationResult:
    """ValidationResult 테스트"""

    def test_default_values(self):
        """기본값 테스트"""
        result = ValidationResult()
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.info == {}

    def test_with_errors(self):
        """에러가 있는 경우"""
        result = ValidationResult(valid=False, errors=["Error 1", "Error 2"])
        assert not result.valid
        assert len(result.errors) == 2

    def test_none_initialization(self):
        """None 값으로 초기화"""
        result = ValidationResult(errors=None, warnings=None, info=None)
        assert result.errors == []
        assert result.warnings == []
        assert result.info == {}
