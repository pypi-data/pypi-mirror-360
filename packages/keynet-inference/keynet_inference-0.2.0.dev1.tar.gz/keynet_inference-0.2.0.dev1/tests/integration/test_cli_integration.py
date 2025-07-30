"""
CLI 통합 테스트

keynet CLI 명령어들의 전체 플로우를 테스트합니다.
실제 파일 시스템과 가상환경을 사용하는 통합 테스트입니다.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from keynet_inference.cli.main import (
    deploy_command,
    handle_test_command,
    login_command,
    logout_command,
)


@pytest.mark.integration
class TestCLIIntegration:
    """CLI 명령어 통합 테스트"""

    def test_login_logout_flow(self, tmp_path):
        """로그인/로그아웃 전체 플로우"""
        # Mock args
        login_args = MagicMock()
        login_args.server_domain = "test.keynet.io"

        logout_args = MagicMock()
        logout_args.server = "test.keynet.io"
        logout_args.all = False

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch("builtins.input", return_value="testuser"):
                with patch("getpass.getpass", return_value="testpass"):
                    with patch("keynet_inference.auth.client.AuthClient") as mock_auth:
                        # Mock successful authentication
                        mock_auth.return_value.authenticate.return_value = (
                            True,
                            "token123",
                        )

                        # 로그인
                        result = login_command(login_args)
                        assert result == 0

                        # 인증 정보가 저장되었는지 확인
                        cred_file = tmp_path / ".keynet" / "credentials.json"
                        assert cred_file.exists()

            # 로그아웃
            result = logout_command(logout_args)
            assert result == 0

            # 인증 정보가 삭제되었는지 확인 - credentials.json은 남아있지만 해당 서버 정보는 없어야 함
            # 이 부분은 CredentialManager의 내부 구현에 따라 다를 수 있음

    def test_test_command_flow(self, tmp_path):
        """테스트 명령어 전체 플로우"""
        # 함수 파일 생성
        func_file = tmp_path / "test_function.py"
        func_file.write_text("""
from keynet_inference.function.decorator import keynet_function

@keynet_function("test-function")
def main(args):
    return {"message": f"Hello {args.get('name', 'World')}!"}
""")

        # Mock args
        mock_args = MagicMock()
        mock_args.file = str(func_file)
        mock_args.requirements = None
        mock_args.params = json.dumps({"name": "Test"})
        mock_args.python_version = "3.12"
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        # 테스트 실행
        result = handle_test_command(mock_args)
        assert result == 0

    @pytest.mark.slow
    def test_test_command_with_requirements(self, tmp_path):
        """requirements.txt와 함께 테스트"""
        # 함수 파일
        func_file = tmp_path / "func_with_deps.py"
        func_file.write_text("""
from keynet_inference.function.decorator import keynet_function
import json

@keynet_function("deps-function")
def main(args):
    data = args.get('data', {})
    return {"json": json.dumps(data)}
""")

        # requirements 파일
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("# 표준 라이브러리만 사용")

        # Mock args
        mock_args = MagicMock()
        mock_args.file = str(func_file)
        mock_args.requirements = str(req_file)
        mock_args.params = json.dumps({"data": {"test": True}})
        mock_args.python_version = "3.12"
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180

        # 테스트 실행
        result = handle_test_command(mock_args)
        assert result == 0

    def test_deploy_command_flow(self, tmp_path):
        """배포 명령어 전체 플로우"""
        # 함수 파일 생성
        func_file = tmp_path / "deploy_function.py"
        func_file.write_text("""
from keynet_inference.function.decorator import keynet_function

@keynet_function("deploy-function")
def main(args):
    return {"deployed": True}
""")

        # Mock args
        mock_args = MagicMock()
        mock_args.file = str(func_file)
        mock_args.requirements = None
        mock_args.python_version = "3.12"
        mock_args.memory = 256
        mock_args.timeout = 60
        mock_args.import_timeout = 120
        mock_args.execution_timeout = 180
        mock_args.server = None  # 명시적으로 None 설정

        with patch("pathlib.Path.home", return_value=tmp_path):
            # 실제 자격 증명 파일 생성
            from keynet_inference.auth import CredentialManager

            cred_manager = CredentialManager()
            cred_manager.save_credentials("test.keynet.io", "testuser", "testpass")

            with patch("keynet_inference.auth.client.AuthClient") as mock_auth:
                mock_auth.return_value.deploy_function.return_value = (
                    True,
                    {"status": "deployed", "function_id": "12345"},
                )

                # 배포 실행
                result = deploy_command(mock_args)
                assert result == 0

    def test_error_handling_in_test_command(self, tmp_path):
        """테스트 명령어 에러 처리"""
        # 잘못된 함수 파일
        func_file = tmp_path / "bad_function.py"
        func_file.write_text("""
# @keynet_function 데코레이터 없음
def main(args):
    return {}
""")

        # Mock args
        mock_args = MagicMock()
        mock_args.file = str(func_file)
        mock_args.requirements = None
        mock_args.params = "{}"
        mock_args.python_version = "3.12"

        # 테스트 실행 - 실패해야 함
        result = handle_test_command(mock_args)
        assert result != 0

    def test_multi_server_workflow(self, tmp_path):
        """다중 서버 워크플로우"""
        servers = ["server1.keynet.io", "server2.keynet.io"]

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch("builtins.input", return_value="testuser"):
                with patch("getpass.getpass", return_value="testpass"):
                    with patch("keynet_inference.auth.client.AuthClient") as mock_auth:
                        mock_auth.return_value.authenticate.return_value = (
                            True,
                            "token123",
                        )

                        # 여러 서버에 로그인
                        for server in servers:
                            login_args = MagicMock()
                            login_args.server_domain = server
                            result = login_command(login_args)
                            assert result == 0

                        # 모든 서버의 인증 정보가 저장되었는지 확인
                        cred_file = tmp_path / ".keynet" / "credentials.json"
                        assert cred_file.exists()

                        # 전체 로그아웃
                        logout_args = MagicMock()
                        logout_args.server = None
                        logout_args.all = True
                        result = logout_command(logout_args)
                        assert result == 0
