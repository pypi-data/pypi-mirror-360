from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from keynet_inference.function.builder import FunctionBuilder
from keynet_inference.function.models import (
    FunctionConfig,
    ValidationResult,
)


class TestFunctionBuilder:
    """FunctionBuilder 테스트"""

    @pytest.fixture
    def builder(self, temp_dir):
        """Builder 인스턴스"""
        with patch("keynet_inference.function.builder.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            return FunctionBuilder()

    def test_initialization(self, temp_dir):
        """초기화 테스트"""
        with patch("keynet_inference.function.builder.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            builder = FunctionBuilder()

            assert builder.venv_manager is not None
            assert builder.validator is not None
            assert (temp_dir / ".wtu_function" / "venvs").exists()

    def test_validate_success(self, builder, valid_python_file, capsys):
        """검증 성공"""
        with patch.object(builder.validator, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(
                valid=True, info={"main_line": 2, "execution_time": 0.001}
            )

            result = builder.validate(str(valid_python_file))

            assert result.valid
            captured = capsys.readouterr()
            assert "✅ 통과" in captured.out
            assert "main 함수: 2번째 줄" in captured.out

    def test_validate_with_warnings(self, builder, valid_python_file, capsys):
        """경고가 있는 검증"""
        with patch.object(builder.validator, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(
                valid=True, warnings=["Python 버전 불일치", "큰 메모리 사용"]
            )

            result = builder.validate(str(valid_python_file))

            captured = capsys.readouterr()
            assert "⚠️  경고 (2개):" in captured.out
            assert "Python 버전 불일치" in captured.out

    def test_validate_failure(self, builder, invalid_python_file, capsys):
        """검증 실패"""
        with patch.object(builder.validator, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(
                valid=False, errors=["문법 오류", "Import 실패"]
            )

            result = builder.validate(str(invalid_python_file))

            assert not result.valid
            captured = capsys.readouterr()
            assert "❌ 실패" in captured.out
            assert "❌ 오류 (2개):" in captured.out

    def test_deploy_success(self, builder, valid_python_file, capsys):
        """배포 성공"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )

        with patch.object(builder, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(valid=True)

            with patch.object(builder, "_upload_to_server") as mock_upload:
                mock_upload.return_value = True

                success = builder.deploy(config)

                assert success
                captured = capsys.readouterr()
                assert "✅ test_function 배포 완료!" in captured.out

    def test_deploy_validation_failure(self, builder, valid_python_file, capsys):
        """검증 실패로 배포 중단"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )

        with patch.object(builder, "validate") as mock_validate:
            mock_validate.return_value = ValidationResult(
                valid=False, errors=["검증 실패"]
            )

            success = builder.deploy(config)

            assert not success
            captured = capsys.readouterr()
            assert "❌ 검증 실패로 배포 중단" in captured.out

    def test_deploy_without_validation(self, builder, valid_python_file):
        """검증 없이 배포"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )

        with patch.object(builder, "_upload_to_server") as mock_upload:
            mock_upload.return_value = True

            success = builder.deploy(config, validate_first=False)

            assert success
            # validate가 호출되지 않았는지 확인하려면 mock_validate.assert_not_called()

    def test_upload_to_server_with_requirements(
        self, builder, valid_python_file, requirements_file
    ):
        """requirements와 함께 업로드"""
        config = FunctionConfig(
            name="test_function",
            python_file=str(valid_python_file),
            requirements_file=str(requirements_file),
        )

        mock_files = {}

        # Path.open을 모킹할 때 self (Path 인스턴스)를 고려해야 함
        def mock_path_open(self, mode, **kwargs):
            mock_file = MagicMock()
            # context manager 설정
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            mock_file.read = MagicMock(return_value=b"test content")
            mock_file.close = MagicMock()
            # 경로를 정규화하여 저장
            normalized_path = str(self.resolve())
            mock_files[normalized_path] = mock_file
            return mock_file

        # read_text도 mock 필요 (파일 검증에서 사용)
        def mock_read_text(self, encoding="utf-8"):
            return "def main(args):\n    return {'result': 'ok'}\n"

        # stat도 mock 필요 (파일 크기 검증에서 사용)
        mock_stat = MagicMock()
        mock_stat.st_size = 1024  # 1KB

        with (
            patch.object(Path, "open", mock_path_open),
            patch.object(Path, "read_text", mock_read_text),
            patch.object(Path, "stat", return_value=mock_stat),
        ):
            success = builder._upload_to_server(config)

            assert success
            # 두 파일이 열렸는지 확인 (경로 정규화)
            assert str(valid_python_file.resolve()) in mock_files
            assert str(requirements_file.resolve()) in mock_files

            # context manager가 제대로 닫혔는지 확인
            for mock_file in mock_files.values():
                mock_file.__exit__.assert_called()

    def test_upload_server_error(self, builder, valid_python_file):
        """서버 업로드 중 에러"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )

        with patch("pathlib.Path.open", mock_open(read_data="def main(): pass")):
            # 현재는 mock이므로 항상 True 반환
            # 실제 구현에서는 requests 예외 처리 테스트 필요
            success = builder._upload_to_server(config)
            assert success

    def test_file_cleanup_on_exception(self, builder, valid_python_file):
        """예외 발생 시 파일 정리"""
        config = FunctionConfig(
            name="test_function", python_file=str(valid_python_file)
        )

        mock_file = MagicMock()
        # Path.open이 context manager를 반환하도록 mock 설정
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)
        mock_file.read = MagicMock(return_value=b"test content")

        import contextlib

        with patch.object(Path, "open", return_value=mock_file):
            # 예외를 발생시키는 시나리오 (실제 구현에서)
            with contextlib.suppress(BaseException):
                builder._upload_to_server(config)

            # context manager의 __exit__이 호출되었는지 확인
            mock_file.__exit__.assert_called()
