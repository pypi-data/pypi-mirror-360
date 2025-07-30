"""Test cases for FunctionBuilder file validation features"""

import tempfile
from pathlib import Path

from keynet_inference.function import FunctionBuilder
from keynet_inference.function.models import FunctionConfig, PythonVersion


class TestFunctionBuilder:
    """Test FunctionBuilder file validation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.builder = FunctionBuilder()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_file_not_exists(self):
        """Test validation with non-existent file"""
        result = self.builder._validate_file("/non/existent/file.py")

        assert not result.valid
        assert len(result.errors) == 1
        assert "파일이 존재하지 않습니다" in result.errors[0]

    def test_validate_file_size_limit(self):
        """Test validation with file exceeding size limit"""
        # Create a file larger than 48MB
        large_file = Path(self.temp_dir) / "large_file.py"
        content = "x" * (49 * 1024 * 1024)  # 49MB
        large_file.write_text(content)

        result = self.builder._validate_file(str(large_file))

        assert not result.valid
        assert len(result.errors) == 1
        assert "파일 크기가 제한을 초과합니다" in result.errors[0]
        assert "49.0MB" in result.errors[0]

    def test_validate_utf8_encoding(self):
        """Test validation with non-UTF8 file"""
        # Create a file with non-UTF8 encoding
        non_utf8_file = Path(self.temp_dir) / "non_utf8.py"
        non_utf8_file.write_bytes(b"\xff\xfe")  # Invalid UTF-8 bytes

        result = self.builder._validate_file(str(non_utf8_file))

        assert not result.valid
        assert len(result.errors) == 1
        assert "UTF-8로 인코딩되지 않았습니다" in result.errors[0]

    def test_validate_security_patterns_exec(self):
        """Test security pattern detection for exec()"""
        dangerous_file = Path(self.temp_dir) / "dangerous.py"
        dangerous_file.write_text(
            """
def main(args):
    user_input = args.get('code', '')
    exec(user_input)  # Dangerous!
    return {"result": "done"}
"""
        )

        result = self.builder._validate_file(str(dangerous_file), "python")

        assert result.valid  # Still valid, but with warnings
        assert len(result.warnings) == 1
        assert "exec() 사용 감지" in result.warnings[0]

    def test_validate_security_patterns_eval(self):
        """Test security pattern detection for eval()"""
        dangerous_file = Path(self.temp_dir) / "eval_usage.py"
        dangerous_file.write_text(
            """
def main(args):
    expression = args.get('expr', '1+1')
    result = eval(expression)
    return {"result": result}
"""
        )

        result = self.builder._validate_file(str(dangerous_file), "python")

        assert result.valid
        assert len(result.warnings) == 1
        assert "eval() 사용 감지" in result.warnings[0]

    def test_validate_security_patterns_subprocess(self):
        """Test security pattern detection for subprocess"""
        dangerous_file = Path(self.temp_dir) / "subprocess_usage.py"
        dangerous_file.write_text(
            """
import subprocess

def main(args):
    cmd = args.get('command', 'ls')
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return {"output": result.stdout.decode()}
"""
        )

        result = self.builder._validate_file(str(dangerous_file), "python")

        assert result.valid
        assert len(result.warnings) == 1
        assert "subprocess 모듈 사용 감지" in result.warnings[0]

    def test_validate_security_patterns_system_file_access(self):
        """Test security pattern detection for system file access"""
        dangerous_file = Path(self.temp_dir) / "system_access.py"
        dangerous_file.write_text(
            """
def main(args):
    with open("/etc/passwd", "r") as f:
        content = f.read()
    return {"content": content}
"""
        )

        result = self.builder._validate_file(str(dangerous_file), "python")

        assert result.valid
        assert len(result.warnings) == 1
        assert "시스템 파일 접근 시도" in result.warnings[0]

    def test_validate_clean_python_file(self):
        """Test validation with clean Python file"""
        clean_file = Path(self.temp_dir) / "clean.py"
        clean_file.write_text(
            """
from keynet_inference.function import keynet_function

@keynet_function("hello-world")
def main(args):
    name = args.get('name', 'World')
    return {"message": f"Hello {name}!"}
"""
        )

        result = self.builder._validate_file(str(clean_file), "python")

        assert result.valid
        assert len(result.warnings) == 0
        assert len(result.errors) == 0
        assert result.info["file_size"] > 0
        assert result.info["line_count"] == 7

    def test_validate_requirements_file(self):
        """Test validation with requirements.txt file"""
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text(
            """requests==2.31.0
numpy>=1.24.0
pandas~=2.0.0
"""
        )

        result = self.builder._validate_file(str(req_file), "requirements")

        assert result.valid
        assert len(result.warnings) == 0  # No security check for requirements
        assert result.info["file_size"] > 0
        assert result.info["line_count"] == 3

    def test_upload_to_server_with_validation_failure(self, monkeypatch, capsys):
        """Test upload fails when file validation fails"""
        # Create a non-UTF8 file
        bad_file = Path(self.temp_dir) / "bad.py"
        bad_file.write_bytes(b"\xff\xfe")

        config = FunctionConfig(
            name="test-function",
            python_file=str(bad_file),
            python_version=PythonVersion.PYTHON_3_12,
            memory=512,
            timeout=60,
        )

        result = self.builder._upload_to_server(config)

        assert not result
        # Check that error message was printed
        captured = capsys.readouterr()
        assert "❌ Python 파일 검증 실패:" in captured.out

    def test_upload_to_server_with_security_warnings(self, monkeypatch, capsys):
        """Test upload continues with security warnings"""
        # Create a file with security warnings
        warning_file = Path(self.temp_dir) / "warning.py"
        warning_file.write_text(
            """
def main(args):
    code = args.get('code', 'print("hello")')
    exec(code)
    return {"status": "executed"}
"""
        )

        config = FunctionConfig(
            name="test-function",
            python_file=str(warning_file),
            python_version=PythonVersion.PYTHON_3_12,
            memory=512,
            timeout=60,
        )

        # The upload should still succeed (mocked to return True)
        result = self.builder._upload_to_server(config)

        assert result  # Should succeed despite warnings
        # Check that warning message was printed
        captured = capsys.readouterr()
        assert "⚠️  보안 경고:" in captured.out

    def test_validate_multiple_security_patterns(self):
        """Test detection of multiple security issues"""
        multi_dangerous_file = Path(self.temp_dir) / "multi_dangerous.py"
        multi_dangerous_file.write_text(
            """
import os
import subprocess

def main(args):
    # Multiple security issues
    user_code = args.get('code', '')
    exec(user_code)

    result = eval(args.get('expr', '1+1'))

    os.system('ls -la')

    with open('/etc/hosts', 'r') as f:
        hosts = f.read()

    return {"status": "done"}
"""
        )

        result = self.builder._validate_file(str(multi_dangerous_file), "python")

        assert result.valid  # Still valid, but with multiple warnings
        assert len(result.warnings) >= 4  # At least 4 security issues

        warning_messages = " ".join(result.warnings)
        assert "exec() 사용 감지" in warning_messages
        assert "eval() 사용 감지" in warning_messages
        assert "os.system() 사용 감지" in warning_messages
        assert "시스템 파일 접근 시도" in warning_messages
