# Valkey Vector App

Valkey의 VectorSearch 기능을 활용한 Python 기반의 QA(질의응답) 애플리케이션입니다.

## 주요 기능
- **문서 임베딩:** `sentence-transformers`를 사용하여 텍스트를 벡터로 변환합니다.
- **벡터 검색:** Valkey의 VectorSearch 모듈을 사용하여 유사한 문서를 검색합니다.
- **REST API:** Flask를 통해 문서 추가 및 검색 API를 제공합니다.

## 환경 설정
- **Docker:** `valkey/valkey-bundle:latest` 이미지를 사용하여 VectorSearch 모듈이 포함된 Valkey를 실행합니다.
- **Python:** 3.8+ 환경에서 동작하며, `requirements.txt`에 명시된 의존성을 설치해야 합니다.

## 실행 방법
1. Valkey 컨테이너 실행:
   ```bash
   docker run -d --name valkey-vector -p 6379:6379 valkey/valkey-bundle:latest
   ```
2. 앱 실행:
   ```bash
   python3 -m src.app
   ```

## 테스트
`pytest`를 사용하여 자동화된 테스트를 수행할 수 있습니다.
