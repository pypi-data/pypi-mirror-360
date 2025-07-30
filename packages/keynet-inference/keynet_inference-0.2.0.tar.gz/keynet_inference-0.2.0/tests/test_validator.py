import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from keynet_inference.function.models import ValidationResult
from keynet_inference.function.validator import FunctionValidator
from keynet_inference.function.venv_manager import VenvManager


class TestFunctionValidator:
    """FunctionValidator 테스트"""

    @pytest.fixture
    def validator(self, temp_dir):
        """Validator 인스턴스"""
        venv_manager = VenvManager(temp_dir)
        return FunctionValidator(venv_manager)

    def test_check_syntax_valid(self, validator, valid_python_file):
        """유효한 문법 검사"""
        result = validator.check_syntax(str(valid_python_file))
        assert result.valid
        assert "main_line" in result.info
        assert result.info["main_args"] == ["args"]

    def test_check_syntax_invalid(self, validator, invalid_python_file):
        """잘못된 문법"""
        result = validator.check_syntax(str(invalid_python_file))
        assert not result.valid
        assert any("문법 오류" in error for error in result.errors)

    def test_check_syntax_no_main(self, validator, no_main_python_file):
        """Main 함수 없음"""
        result = validator.check_syntax(str(no_main_python_file))
        assert not result.valid
        assert any("main 함수를 찾을 수 없습니다" in error for error in result.errors)

    def test_check_syntax_file_not_found(self, validator):
        """파일을 찾을 수 없음"""
        result = validator.check_syntax("/nonexistent/file.py")
        assert not result.valid
        assert any("파일 읽기 오류" in error for error in result.errors)

    def test_check_syntax_empty_file(self, validator, temp_dir):
        """빈 파일"""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")

        result = validator.check_syntax(str(empty_file))
        assert not result.valid
        assert any("main 함수를 찾을 수 없습니다" in error for error in result.errors)

    @patch("subprocess.run")
    def test_test_import_success(self, mock_run, validator, temp_dir):
        """Import 성공 테스트"""
        mock_run.return_value = MagicMock(returncode=0, stdout="SUCCESS", stderr="")

        venv_path = temp_dir / "test_venv"
        venv_path.mkdir()

        result = validator.test_import(venv_path, "test.py")
        assert result.valid

    @patch("subprocess.run")
    def test_test_import_failure(self, mock_run, validator, temp_dir):
        """Import 실패 테스트"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="ModuleNotFoundError: No module named 'missing_module'",
        )

        venv_path = temp_dir / "test_venv"
        venv_path.mkdir()

        result = validator.test_import(venv_path, "test.py")
        assert not result.valid
        assert any("Import 실패" in error for error in result.errors)

    @patch("subprocess.run")
    def test_test_execution_success(self, mock_run, validator, temp_dir):
        """실행 성공 테스트"""
        test_output = {
            "success": True,
            "result": {"greeting": "Hello World!"},
            "time": 0.001,
        }

        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(test_output), stderr=""
        )

        venv_path = temp_dir / "test_venv"
        venv_path.mkdir()

        result = validator.test_execution(venv_path, "test.py", {"name": "World"})

        assert result.valid
        assert result.info["execution_time"] == 0.001
        assert result.info["test_result"] == {"greeting": "Hello World!"}

    @patch("subprocess.run")
    def test_test_execution_runtime_error(self, mock_run, validator, temp_dir):
        """실행 중 에러"""
        test_output = {"success": False, "error": "TypeError: expected string"}

        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(test_output), stderr=""
        )

        venv_path = temp_dir / "test_venv"
        venv_path.mkdir()

        result = validator.test_execution(venv_path, "test.py", {})
        assert not result.valid
        assert any("TypeError: expected string" in error for error in result.errors)

    @patch("subprocess.run")
    def test_test_execution_json_error(self, mock_run, validator, temp_dir):
        """JSON 파싱 에러"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Invalid JSON", stderr="Some error"
        )

        venv_path = temp_dir / "test_venv"
        venv_path.mkdir()

        result = validator.test_execution(venv_path, "test.py", {})
        assert not result.valid
        assert any("실행 오류" in error for error in result.errors)

    def test_validate_full_success(self, validator, valid_python_file):
        """전체 검증 성공"""
        with patch.object(validator.venv_manager, "get_or_create") as mock_venv:
            venv_path = Path("/fake/venv")
            mock_venv.return_value = (venv_path, False)

            with patch.object(validator, "test_import") as mock_import:
                mock_import.return_value = ValidationResult(valid=True)

                with patch.object(validator, "test_execution") as mock_exec:
                    mock_exec.return_value = ValidationResult(
                        valid=True, info={"execution_time": 0.1}
                    )

                    result = validator.validate(
                        str(valid_python_file), test_params={"name": "Test"}
                    )

                    assert result.valid
                    assert result.info["venv_cached"] is False
                    assert result.info["execution_time"] == 0.1

    def test_validate_syntax_failure(self, validator, invalid_python_file):
        """문법 오류로 검증 실패"""
        result = validator.validate(str(invalid_python_file))
        assert not result.valid
        # 문법 검사에서 실패하면 다른 테스트는 실행되지 않음

    def test_validate_import_failure(self, validator, valid_python_file):
        """Import 실패"""
        with patch.object(validator.venv_manager, "get_or_create") as mock_venv:
            venv_path = Path("/fake/venv")
            mock_venv.return_value = (venv_path, False)

            with patch.object(validator, "test_import") as mock_import:
                mock_import.return_value = ValidationResult(
                    valid=False, errors=["Import failed"]
                )

                result = validator.validate(
                    str(valid_python_file), requirements_file="requirements.txt"
                )

                assert not result.valid

    def test_path_injection_protection(self, validator, temp_dir):
        """경로 인젝션 보호"""
        # 악의적인 파일명 (파일 시스템이 허용하는 문자 사용)
        malicious_file = temp_dir / "test_semicolon_rm_rf.py"
        malicious_file.write_text("def main(args): pass")

        # 파일명에 특수문자가 있어도 안전하게 처리되어야 함
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="SUCCESS", stderr="")

            result = validator.test_import(temp_dir, str(malicious_file))

            # subprocess.run이 올바른 인자로 호출되었는지 확인
            args = mock_run.call_args[0][0]
            assert str(malicious_file) in args  # 안전하게 전달됨
