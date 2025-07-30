import hashlib
import json
import platform
import subprocess
import sys
from unittest.mock import patch

import pytest

from keynet_inference.function.venv_manager import VenvManager


class TestVenvManager:
    """VenvManager 테스트"""

    def test_initialization(self, temp_dir):
        """초기화 테스트"""
        manager = VenvManager(temp_dir)
        assert manager.cache_dir == temp_dir / "venvs"
        assert manager.cache_dir.exists()

    def test_venv_path_generation_no_requirements(self, temp_dir):
        """Requirements 없을 때 경로 생성"""
        manager = VenvManager(temp_dir)
        path = manager._get_venv_path(None, "3.12")
        assert path == temp_dir / "venvs" / "python3.12_base"

    def test_venv_path_generation_with_requirements(self, temp_dir, requirements_file):
        """Requirements 있을 때 경로 생성"""
        manager = VenvManager(temp_dir)
        path = manager._get_venv_path(str(requirements_file), "3.12")

        # 해시 검증
        with requirements_file.open("rb") as f:
            expected_hash = hashlib.md5(f.read()).hexdigest()[:8]

        assert f"python3.12_{expected_hash}" in str(path)

    @pytest.mark.slow
    def test_create_venv_without_requirements(self, temp_dir):
        """Requirements 없이 venv 생성"""
        manager = VenvManager(temp_dir)
        venv_path, cached = manager.get_or_create(None, "3.12")

        assert venv_path.exists()
        assert not cached
        assert (venv_path / ("Scripts" if sys.platform == "win32" else "bin")).exists()

        # 캐시 테스트
        venv_path2, cached2 = manager.get_or_create(None, "3.12")
        assert cached2
        assert venv_path == venv_path2

    @pytest.mark.slow
    def test_create_venv_with_requirements(self, temp_dir):
        """requirements와 함께 venv 생성 및 패키지 설치"""
        manager = VenvManager(temp_dir)

        # 빈 requirements 파일 생성 (설치 테스트만)
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("")  # 빈 파일

        venv_path, cached = manager.get_or_create(str(req_file))

        assert venv_path.exists()
        assert not cached

        # pip 실행 가능한지 확인
        pip_path = manager._get_pip_path(venv_path)
        assert pip_path.exists()

        # venv가 생성되었는지 확인
        python_path = manager.get_python_path(venv_path)
        assert python_path.exists()

    def test_pip_path_windows(self, temp_dir):
        """Windows pip 경로"""
        manager = VenvManager(temp_dir)
        venv_path = temp_dir / "test_venv"

        with patch("sys.platform", "win32"):
            pip_path = manager._get_pip_path(venv_path)
            assert pip_path == venv_path / "Scripts" / "pip.exe"

    def test_pip_path_unix(self, temp_dir):
        """Unix pip 경로"""
        manager = VenvManager(temp_dir)
        venv_path = temp_dir / "test_venv"

        with patch("sys.platform", "linux"):
            pip_path = manager._get_pip_path(venv_path)
            assert pip_path == venv_path / "bin" / "pip"

    def test_python_path_windows(self, temp_dir):
        """Windows python 경로"""
        manager = VenvManager(temp_dir)
        venv_path = temp_dir / "test_venv"

        with patch("sys.platform", "win32"):
            python_path = manager.get_python_path(venv_path)
            assert python_path == venv_path / "Scripts" / "python.exe"

    def test_python_path_unix(self, temp_dir):
        """Unix python 경로"""
        manager = VenvManager(temp_dir)
        venv_path = temp_dir / "test_venv"

        with patch("sys.platform", "linux"):
            python_path = manager.get_python_path(venv_path)
            assert python_path == venv_path / "bin" / "python"

    def test_requirements_install_failure(self, temp_dir):
        """Requirements 설치 실패"""
        manager = VenvManager(temp_dir)

        # 잘못된 requirements
        bad_req = temp_dir / "bad_requirements.txt"
        bad_req.write_text("nonexistent-package-12345==99.99.99")

        with pytest.raises(RuntimeError, match="Requirements 설치 실패"):
            manager.get_or_create(str(bad_req), "3.12")

        # 실패한 venv가 삭제되었는지 확인
        venv_path = manager._get_venv_path(str(bad_req), "3.12")
        assert not venv_path.exists()

    def test_get_installed_packages_error(self, temp_dir):
        """패키지 목록 가져오기 실패"""
        manager = VenvManager(temp_dir)
        fake_venv = temp_dir / "fake_venv"
        fake_venv.mkdir()

        packages = manager.get_installed_packages(fake_venv)
        assert packages == {}

    def test_concurrent_venv_creation(self, temp_dir):
        """동시에 같은 venv 생성 시도"""
        import threading

        manager = VenvManager(temp_dir)
        results = []

        def create_venv():
            try:
                path, cached = manager.get_or_create(None, "3.12")
                results.append((path, cached, None))
            except Exception as e:
                results.append((None, None, e))

        # 두 스레드가 동시에 생성 시도
        threads = [threading.Thread(target=create_venv) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 하나는 성공하고 하나는 캐시되거나 둘 다 성공해야 함
        assert len(results) == 2
        assert all(r[0] is not None for r in results)  # 둘 다 경로를 받아야 함

    def test_cross_platform_paths(self, temp_dir):
        """크로스 플랫폼 경로 처리"""
        manager = VenvManager(temp_dir)
        venv_path = temp_dir / "test_venv"

        pip_path = manager._get_pip_path(venv_path)
        python_path = manager.get_python_path(venv_path)

        if platform.system() == "Windows":
            assert str(pip_path).endswith("Scripts\\pip.exe") or str(pip_path).endswith(
                "Scripts/pip.exe"
            )
            assert str(python_path).endswith("Scripts\\python.exe") or str(
                python_path
            ).endswith("Scripts/python.exe")
        else:
            assert str(pip_path).endswith("bin/pip")
            assert str(python_path).endswith("bin/python")

    @pytest.mark.slow
    def test_real_package_execution(self, temp_dir):
        """실제 패키지 설치 후 함수 실행 테스트"""
        manager = VenvManager(temp_dir)

        # JSON 처리를 위한 간단한 함수
        func_file = temp_dir / "json_func.py"
        func_file.write_text(
            """
import json

def main(args):
    data = args.get('data', {})
    return {"json_string": json.dumps(data), "keys": list(data.keys())}
"""
        )

        # venv 생성 (requirements 없이)
        venv_path, _ = manager.get_or_create()
        python_path = manager.get_python_path(venv_path)

        # 함수 실행
        test_data = {"name": "test", "value": 123}
        result = subprocess.run(
            [
                str(python_path),
                "-c",
                f"""
import sys
import json
sys.path.insert(0, r'{temp_dir}')
from json_func import main
test_data = {json.dumps(test_data)}
result = main({{"data": test_data}})  # args로 전달해야 함
print(json.dumps(result))
""",
            ],
            capture_output=True,
            text=True,
        )

        # 디버깅용 출력
        if result.returncode != 0:
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "json_string" in output
        assert set(output["keys"]) == {"name", "value"}
