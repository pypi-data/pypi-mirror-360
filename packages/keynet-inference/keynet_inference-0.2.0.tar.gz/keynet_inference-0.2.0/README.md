# keynet-inference

Triton Inference Server 통합과 보안 함수 실행을 위한 추론 유틸리티

## 설치

```bash
pip install keynet-inference
```

## 주요 기능

### 🔌 MLflow-Triton 통합

- MLflow 모델을 Triton Inference Server로 자동 배포
- Python 함수를 Triton 모델로 변환
- S3/MinIO 기반 모델 저장소 지원

### 🛡️ 보안 함수 실행

- 격리된 가상환경에서 안전한 실행
- 메모리 및 CPU 사용량 제한
- 타임아웃 기반 실행 제어

### 🛠️ Keynet CLI

- 함수 검증 및 테스트
- 배포 자동화
- 인증 관리
- Python 3.9~3.12 지원

## 사용 예제

### Python 함수 작성

```python
from keynet_inference.function import keynet_function

@keynet_function(
    python_version="3.11",
    requirements=["numpy", "pandas"],
    timeout=30
)
def process_data(args):
    """데이터 처리 함수"""
    data = args.get("data", [])
    result = sum(data) / len(data) if data else 0

    return {
        "result": result,
        "count": len(data)
    }
```

### CLI 사용

```bash
# 함수 검증
keynet validate my_function.py

# 테스트 실행
keynet test my_function.py --params '{"data": [1, 2, 3, 4, 5]}'

# 배포
keynet deploy my_function.py --name my_model

# 인증 관리
keynet login https://api.example.com
keynet logout --all
```

### MLflow 플러그인 사용

```python
import mlflow
from keynet_inference import TritonPlugin

# Triton으로 모델 배포
mlflow.deployments.create_deployment(
    name="my-deployment",
    model_uri="models:/my_model/1",
    flavor="triton",
    config={
        "triton_url": "localhost:8001",
        "model_repository": "s3://models"
    }
)
```

## API 문서

자세한 API 문서는 [GitHub Wiki](https://github.com/WIM-Corporation/keynet/wiki) 참조

## 라이선스

MIT License
