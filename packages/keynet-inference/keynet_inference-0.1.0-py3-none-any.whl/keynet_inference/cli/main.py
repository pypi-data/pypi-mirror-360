"""
Command Line Interface for Keynet Function Builder

This module provides CLI commands for managing serverless functions
with the @keynet_function decorator.
"""

import argparse
import getpass
import json
import sys

from keynet_inference.auth import AuthClient, CredentialManager
from keynet_inference.function import FunctionBuilder, FunctionConfig


def login_command(args):
    """Handle the login command"""
    server_domain = args.server_domain

    # Normalize server domain (remove protocol if provided)
    if server_domain.startswith("http://"):
        server_domain = server_domain[7:]
    elif server_domain.startswith("https://"):
        server_domain = server_domain[8:]

    print(f"🔐 Keynet 서버에 로그인: {server_domain}")

    # Prompt for credentials
    username = input("사용자명: ")
    if not username:
        print("❌ 사용자명을 입력해주세요.")
        return 1

    password = getpass.getpass("비밀번호: ")
    if not password:
        print("❌ 비밀번호를 입력해주세요.")
        return 1

    # Authenticate with server
    auth_client = AuthClient(server_domain)
    success, result = auth_client.authenticate(username, password)

    if success:
        # Save credentials
        credential_manager = CredentialManager()
        credential_manager.save_credentials(server_domain, username, password)
        print(f"✅ 로그인 성공! [{username}@{server_domain}]")
        return 0
    else:
        print(f"❌ 로그인 실패: {result}")
        return 1


def logout_command(args):
    """Handle the logout command"""
    credential_manager = CredentialManager()

    if args.all:
        # Remove all credentials
        credential_manager.remove_credentials()
        print("✅ 모든 로그인 정보가 삭제되었습니다.")
    else:
        # List servers if no specific server provided
        servers = credential_manager.list_servers()
        if not servers:
            print("💭 저장된 로그인 정보가 없습니다.")
            return 0

        if args.server:
            # Remove specific server
            if args.server in servers:
                credential_manager.remove_credentials(args.server)
                print(f"✅ {args.server}에 대한 로그인 정보가 삭제되었습니다.")
            else:
                print(f"❌ {args.server}에 대한 로그인 정보가 없습니다.")
                return 1
        else:
            # Show current logins
            print("🔑 현재 로그인 정보:")
            for i, server in enumerate(servers, 1):
                creds = credential_manager.get_credentials(server)
                if creds:
                    username, _ = creds
                    print(f"   {i}. {username}@{server}")

    return 0


def handle_test_command(args):
    """Handle the test command (validate function)"""
    builder = FunctionBuilder(
        import_timeout=args.import_timeout, execution_timeout=args.execution_timeout
    )

    # Parse test parameters if provided
    test_params = None
    if args.params:
        try:
            test_params = json.loads(args.params)
        except json.JSONDecodeError:
            print("❌ 오류: --params는 유효한 JSON 형식이어야 합니다")
            return 1

    result = builder.validate(
        python_file=args.file,
        requirements_file=args.requirements,
        test_params=test_params,
    )

    return 0 if result.valid else 1


def deploy_command(args):
    """Handle the deploy command"""
    # Check credentials first
    credential_manager = CredentialManager()
    servers = credential_manager.list_servers()

    if not servers:
        print("❌ 로그인 정보가 없습니다. 먼저 'keynet login' 명령어를 실행해주세요.")
        return 1

    # Use the most recent server or specified server
    if hasattr(args, "server") and args.server:
        server_domain = args.server
        if server_domain not in servers:
            print(f"❌ {server_domain}에 대한 로그인 정보가 없습니다.")
            print(f"   사용 가능한 서버: {', '.join(servers)}")
            return 1
    else:
        server_domain = servers[-1]  # Most recent

    # Get credentials
    creds = credential_manager.get_credentials(server_domain)
    if not creds:
        print(f"❌ {server_domain}에 대한 인증 정보를 가져올 수 없습니다.")
        return 1

    username, _ = creds
    print(f"🌐 배포 서버: {server_domain} ({username})")

    builder = FunctionBuilder(
        import_timeout=args.import_timeout, execution_timeout=args.execution_timeout
    )

    # First validate to get the function name from decorator
    print("🔍 함수 정보 추출 중...")
    validation_result = builder.validator.check_syntax(args.file)

    if not validation_result.valid:
        print("❌ 함수 검증 실패:")
        for error in validation_result.errors:
            print(f"   - {error}")
        return 1

    # Get function name from decorator
    if "keynet_function_name" not in validation_result.info:
        print("❌ 오류: @keynet_function 데코레이터에서 함수 이름을 찾을 수 없습니다")
        return 1

    function_name = validation_result.info["keynet_function_name"]
    print(f"📦 함수 이름: {function_name}")

    # Create FunctionConfig
    try:
        config = FunctionConfig(
            name=function_name,
            python_file=args.file,
            requirements_file=args.requirements,
            python_version=args.python_version,
            memory=args.memory,
            timeout=args.timeout,
        )
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        return 1

    # TODO: Get auth token and pass to deploy
    # auth_client = AuthClient(server_domain)
    # token = auth_client.get_token(username, password)

    # Deploy without full validation (user should run test first)
    success = builder.deploy(config=config, validate_first=False)

    return 0 if success else 1


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        prog="keynet",
        description="Keynet - 서버리스 함수 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
    # Keynet 서버 로그인
    keynet login <Keynet Server>

    # 현재 로그인 정보 확인
    keynet logout

    # 함수 테스트
    keynet test function.py
    keynet test function.py --params '{"name": "World"}'

    # 함수 배포 (@keynet_function 데코레이터에서 이름을 가져옴)
    keynet deploy function.py
    keynet deploy function.py --python-version 3.12
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")

    # Login command
    login_parser = subparsers.add_parser(
        "login",
        help="Keynet 서버에 로그인",
        description="사용자명과 비밀번호를 사용하여 Keynet 서버에 인증합니다.",
    )
    login_parser.add_argument(
        "server_domain", help="서버 도메인 (예: api.keynet.io)", metavar="SERVER_DOMAIN"
    )

    # Logout command
    logout_parser = subparsers.add_parser(
        "logout",
        help="Keynet 서버에서 로그아웃",
        description="저장된 로그인 정보를 삭제합니다.",
    )
    logout_parser.add_argument(
        "-s", "--server", help="특정 서버의 로그인 정보만 삭제", metavar="SERVER"
    )
    logout_parser.add_argument(
        "--all", action="store_true", help="모든 로그인 정보 삭제"
    )

    # Test command (validate)
    test_parser = subparsers.add_parser(
        "test",
        help="함수 테스트 (로컬 검증)",
        description="함수의 문법, 구조, 실행 가능성을 검증합니다.",
    )
    test_parser.add_argument("file", help="테스트할 Python 파일 경로")
    test_parser.add_argument(
        "-r", "--requirements", help="requirements.txt 파일 경로", metavar="FILE"
    )
    test_parser.add_argument(
        "-p", "--params", help="테스트 파라미터 (JSON 형식)", metavar="JSON"
    )
    test_parser.add_argument(
        "--import-timeout",
        type=int,
        default=120,
        help="import 타임아웃 (초, 기본값: 120)",
    )
    test_parser.add_argument(
        "--execution-timeout",
        type=int,
        default=180,
        help="실행 타임아웃 (초, 기본값: 180)",
    )

    # Deploy command
    deploy_parser = subparsers.add_parser(
        "deploy", help="함수 배포", description="함수를 Keynet 서버에 배포합니다."
    )
    deploy_parser.add_argument("file", help="배포할 Python 파일 경로")
    deploy_parser.add_argument(
        "-r", "--requirements", help="requirements.txt 파일 경로", metavar="FILE"
    )
    deploy_parser.add_argument(
        "--python-version",
        choices=["3.9", "3.10", "3.11", "3.12"],
        default="3.12",
        help="Python 버전 (기본값: 3.12)",
    )
    deploy_parser.add_argument(
        "--memory", type=int, default=512, help="메모리 크기 (MB, 기본값: 512)"
    )
    deploy_parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="패키지 업로드 타임아웃 (초, 기본값: 60)",
    )
    deploy_parser.add_argument(
        "--import-timeout",
        type=int,
        default=120,
        help="import 타임아웃 (초, 기본값: 120)",
    )
    deploy_parser.add_argument(
        "--execution-timeout",
        type=int,
        default=180,
        help="실행 타임아웃 (초, 기본값: 180)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "login":
        return login_command(args)
    elif args.command == "logout":
        return logout_command(args)
    elif args.command == "test":
        return handle_test_command(args)
    elif args.command == "deploy":
        return deploy_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
