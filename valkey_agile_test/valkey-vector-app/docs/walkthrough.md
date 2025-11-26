# Valkey Vector App 설정 및 테스트 결과

## 개요
Valkey Vector App의 환경을 설정하고, 자동화된 테스트와 수동 검증을 수행했습니다. 초기 계획과 달리 `valkey/valkey:latest` 대신 `valkey/valkey-bundle:latest` 이미지를 사용하여 벡터 검색 모듈(`search`)을 활성화했습니다.

## 변경 사항
- **Docker 이미지:** `valkey/valkey:latest` -> `valkey/valkey-bundle:latest`
    - 사유: 기본 이미지에 `vectorsearch.so` 모듈이 포함되어 있지 않아, 모듈이 번들된 이미지를 사용했습니다.

## 테스트 결과

### 1. 자동화 테스트 (`pytest`)
- **결과:** 4 passed, 1 skipped
- **내용:**
    - `tests/test_app.py`: 2 passed, 1 skipped (UI 테스트는 수동 검증으로 대체)
    - `tests/test_db.py`: 1 passed
    - `tests/test_embedding.py`: 1 passed

```bash
tests/test_app.py s..                                                    [ 60%]
tests/test_db.py .                                                       [ 80%]
tests/test_embedding.py .                                                [100%]
```

### 2. 수동 검증
Flask 애플리케이션을 실행하고 `curl`을 사용하여 API 엔드포인트를 검증했습니다.

#### 문서 추가 (`/add_document`)
- **요청:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"document": "Valkey is a high-performance key-value store."}' http://127.0.0.1:5000/add_document
    ```
- **응답:**
    ```json
    {
      "doc_id": "b1705916-bcf5-4018-967c-e914a9e9312e",
      "message": "Document added successfully"
    }
    ```

#### 질문 검색 (`/qa`)
- **요청:**
    ```bash
    curl "http://127.0.0.1:5000/qa?question=What%20is%20Valkey?"
    ```
- **응답:**
    ```json
    {
      "answer": "Valkey is a high-performance key-value store."
    }
    ```

## 결론
Valkey Vector App이 정상적으로 설정되었으며, 벡터 검색 기능이 올바르게 작동함을 확인했습니다.
