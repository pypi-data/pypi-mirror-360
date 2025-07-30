# keynet-core

Keynet 패키지들의 핵심 유틸리티와 공통 모델

## 설치

```bash
pip install keynet-core
```

## 주요 기능

### 🔧 공통 유틸리티

- 환경 변수 관리
- 설정 파일 처리
- 로깅 설정

### 📦 공유 모델

- 데이터 검증 모델
- API 응답 모델
- 설정 스키마

### 🔌 의존성

- 최소한의 의존성 유지
- 다른 Keynet 패키지의 기반

## 사용 예제

```python
from keynet_core import Config, check_env

# 환경 변수 검증
if check_env():
    print("필수 환경 변수 설정 완료")

# 설정 로드
config = Config()
print(f"MLflow URI: {config.mlflow_tracking_uri}")
```

## API 문서

자세한 API 문서는 [GitHub Wiki](https://github.com/WIM-Corporation/keynet/wiki) 참조

## 라이선스

MIT License
