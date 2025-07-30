# venv_manager.py
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


class VenvManager:
    """가상환경 관리자"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "venvs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_or_create(
        self, requirements_file: Optional[str] = None, python_version: str = "3.12"
    ) -> tuple[Path, bool]:
        """캐시된 venv 반환 또는 새로 생성"""
        venv_path = self._get_venv_path(requirements_file, python_version)

        if venv_path.exists():
            return venv_path, True

        # 새 venv 생성
        # 시스템 Python을 우선 사용하도록 시도
        python_executables = [
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            sys.executable,
        ]

        created = False
        for python_exe in python_executables:
            if Path(python_exe).exists():
                try:
                    result = subprocess.run(
                        [python_exe, "-m", "venv", str(venv_path)],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        created = True
                        break
                except Exception:
                    continue

        if not created:
            raise RuntimeError(
                "가상환경 생성 실패: 적절한 Python 실행파일을 찾을 수 없습니다"
            )

        if requirements_file:
            self._install_requirements(venv_path, requirements_file)

        return venv_path, False

    def _get_venv_path(
        self, requirements_file: Optional[str], python_version: str
    ) -> Path:
        """Venv 경로 생성"""
        if not requirements_file:
            return self.cache_dir / f"python{python_version}_base"

        # requirements 파일 해시로 고유 경로 생성
        with Path(requirements_file).open("rb") as f:
            content_hash = hashlib.md5(f.read()).hexdigest()[:8]

        return self.cache_dir / f"python{python_version}_{content_hash}"

    def _install_requirements(self, venv_path: Path, requirements_file: str) -> bool:
        """Requirements 설치"""
        pip_path = self._get_pip_path(venv_path)

        # pip 업그레이드 추가
        subprocess.run(
            [str(pip_path), "install", "--upgrade", "pip"], capture_output=True
        )

        result = subprocess.run(
            [str(pip_path), "install", "-r", requirements_file],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # 실패한 venv 삭제
            import shutil

            shutil.rmtree(venv_path)
            raise RuntimeError(f"Requirements 설치 실패: {result.stderr}")

        return True

    def _get_pip_path(self, venv_path: Path) -> Path:
        """플랫폼별 pip 경로"""
        if sys.platform == "win32":
            return venv_path / "Scripts" / "pip.exe"
        return venv_path / "bin" / "pip"

    def get_python_path(self, venv_path: Path) -> Path:
        """플랫폼별 python 경로"""
        if sys.platform == "win32":
            return venv_path / "Scripts" / "python.exe"
        return venv_path / "bin" / "python"

    def get_installed_packages(self, venv_path: Path) -> dict[str, str]:
        """설치된 패키지 목록"""
        pip_path = self._get_pip_path(venv_path)

        # pip가 존재하지 않으면 빈 딕셔너리 반환
        if not pip_path.exists():
            return {}

        result = subprocess.run(
            [str(pip_path), "list", "--format=json"], capture_output=True, text=True
        )

        packages = {}
        if result.returncode == 0:
            try:
                package_list = json.loads(result.stdout)
                for pkg in package_list:
                    packages[pkg["name"]] = pkg["version"]
            except Exception:
                # fallback to freeze format
                result = subprocess.run(
                    [str(pip_path), "freeze"], capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split("\n"):
                        if "==" in line:
                            name, version = line.split("==", 1)
                            packages[name] = version

        return packages
