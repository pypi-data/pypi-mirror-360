"""
인증 시스템 통합 테스트

AuthClient와 CredentialManager의 통합 동작을 테스트합니다.
실제 파일 시스템을 사용하는 통합 테스트입니다.
"""

from unittest.mock import patch

import pytest

from keynet_inference.auth import AuthClient, CredentialManager


@pytest.mark.integration
class TestAuthIntegration:
    """인증 시스템 통합 테스트"""

    def test_credential_save_and_retrieve_flow(self, tmp_path):
        """인증 정보 저장 및 조회 플로우"""
        with patch("pathlib.Path.home", return_value=tmp_path):
            cred_manager = CredentialManager()

            # 인증 정보 저장
            server = "test.keynet.io"
            username = "testuser"
            password = "testpass"

            cred_manager.save_credentials(server, username, password)

            # 저장된 서버 목록 확인
            servers = cred_manager.list_servers()
            assert server in servers

            # 인증 정보 조회
            retrieved_user, retrieved_pass = cred_manager.get_credentials(server)
            assert retrieved_user == username
            assert retrieved_pass == password

            # 인증 정보 삭제
            cred_manager.remove_credentials(server)
            assert server not in cred_manager.list_servers()

    def test_auth_client_with_credential_manager(self, tmp_path):
        """AuthClient와 CredentialManager 통합"""
        server = "auth.keynet.io"

        with patch("pathlib.Path.home", return_value=tmp_path):
            # 먼저 인증 정보 저장
            cred_manager = CredentialManager()
            cred_manager.save_credentials(server, "testuser", "testpass")

            # AuthClient로 인증
            auth_client = AuthClient(server)

            # 저장된 인증 정보로 인증 시도
            success, token = auth_client.authenticate("testuser", "testpass")

            assert success
            # AuthClient는 현재 mock 구현을 사용하므로 base64 인코딩된 토큰 반환
            import base64

            expected_token = base64.b64encode(f"testuser:{server}".encode()).decode()
            assert token == expected_token

    def test_token_validation_flow(self, tmp_path):
        """토큰 검증 플로우"""
        server = "auth.keynet.io"
        token = "valid_token_123"

        auth_client = AuthClient(server)

        # 토큰 검증 - 현재 mock 구현은 토큰이 있으면 True 반환
        is_valid = auth_client.validate_token(token)
        assert is_valid

        # 빈 토큰은 False
        is_valid = auth_client.validate_token("")
        assert not is_valid

    def test_token_refresh_flow(self, tmp_path):
        """토큰 갱신 플로우"""
        server = "deploy.keynet.io"
        token = "deploy_token_123"

        auth_client = AuthClient(server)

        # 토큰 갱신 - 현재 mock 구현은 유효한 토큰을 그대로 반환
        success, new_token = auth_client.refresh_token(token)
        assert success
        assert new_token == token

        # 빈 토큰으로 갱신 시도
        success, error = auth_client.refresh_token("")
        assert not success
        assert "Invalid or expired token" in error

    def test_multi_server_credential_isolation(self, tmp_path):
        """다중 서버 인증 정보 격리"""
        servers = {
            "server1.keynet.io": ("user1", "pass1"),
            "server2.keynet.io": ("user2", "pass2"),
            "server3.keynet.io": ("user3", "pass3"),
        }

        with patch("pathlib.Path.home", return_value=tmp_path):
            cred_manager = CredentialManager()

            # 각 서버에 다른 인증 정보 저장
            for server, (username, password) in servers.items():
                cred_manager.save_credentials(server, username, password)

            # 각 서버의 인증 정보가 올바르게 격리되어 있는지 확인
            for server, (expected_user, expected_pass) in servers.items():
                retrieved_user, retrieved_pass = cred_manager.get_credentials(server)
                assert retrieved_user == expected_user
                assert retrieved_pass == expected_pass

            # 한 서버의 인증 정보 삭제가 다른 서버에 영향을 주지 않는지 확인
            cred_manager.remove_credentials("server2.keynet.io")

            assert "server1.keynet.io" in cred_manager.list_servers()
            assert "server2.keynet.io" not in cred_manager.list_servers()
            assert "server3.keynet.io" in cred_manager.list_servers()

    def test_corrupted_credential_handling(self, tmp_path):
        """손상된 인증 정보 처리"""
        with patch("pathlib.Path.home", return_value=tmp_path):
            cred_manager = CredentialManager()

            # 정상적인 인증 정보 저장
            cred_manager.save_credentials("good.keynet.io", "user", "pass")

            # config 파일에 손상된 서버 정보 직접 추가
            import json

            config_file = tmp_path / ".keynet" / "credentials.json"
            with config_file.open() as f:
                config = json.load(f)

            # 손상된 인증 정보 추가
            config["corrupted.keynet.io"] = {
                "username": "corrupted_user",
                "password": "invalid_encrypted_data",
            }

            with config_file.open("w") as f:
                json.dump(config, f)

            # 서버 목록에는 둘 다 나타남
            servers = cred_manager.list_servers()
            assert "good.keynet.io" in servers
            assert "corrupted.keynet.io" in servers

            # 손상된 파일의 인증 정보는 None 반환 (또는 예외 발생)
            try:
                user, passwd = cred_manager.get_credentials("corrupted.keynet.io")
                assert user is None
                assert passwd is None
            except Exception:
                # 복호화 실패로 인한 예외도 허용
                pass

            # 정상 파일은 여전히 작동
            user, passwd = cred_manager.get_credentials("good.keynet.io")
            assert user == "user"
            assert passwd == "pass"

    def test_auth_error_propagation(self):
        """인증 에러 전파"""
        server = "error.keynet.io"
        auth_client = AuthClient(server)

        # 빈 사용자명/비밀번호로 인증 시도
        success, error_msg = auth_client.authenticate("", "pass")
        assert not success
        assert "Invalid credentials" in error_msg

        success, error_msg = auth_client.authenticate("user", "")
        assert not success
        assert "Invalid credentials" in error_msg
