# Sprint 2: Ollama 임베딩 연동 수동 테스트 가이드

이 문서는 Sprint 2에서 구현된 **Ollama 임베딩 연동** 및 **인덱스 자동 차원 변경** 기능을 사용자가 직접 확인하는 절차를 안내합니다.

## 1. 사전 준비 사항 (Prerequisites)

테스트를 시작하기 전에 다음 항목들이 준비되어 있어야 합니다.

1.  **Ollama 설치 및 모델 다운로드**
    *   로컬 환경에 Ollama가 설치되어 있어야 합니다.
    *   `nomic-embed-text` 모델을 다운로드합니다.
    ```bash
    ollama pull nomic-embed-text
    ```
    *   Ollama 서비스가 실행 중인지 확인합니다 (기본 포트: 11434).

2.  **인프라 구동 (Docker)**
    *   Postgres와 Valkey 컨테이너가 실행 중이어야 합니다.
    ```bash
    cd usecase_rag_highperf
    docker compose up -d
    ```

3.  **Python 가상환경 및 의존성**
    *   `requests` 라이브러리가 포함된 최신 의존성이 설치되어 있어야 합니다.
    ```bash
    source .venv/bin/activate
    pip install -r app/requirements.txt
    ```

4.  **환경 변수 (.env)**
    *   `.env` 파일에 `OLLAMA_BASE_URL`이 설정되어 있는지 확인합니다.
    ```properties
    OLLAMA_BASE_URL=http://localhost:11434
    ```

---

## 2. 테스트 단계 (Step-by-Step)

### Step 1: 단위 테스트로 기능 검증
가장 먼저 코드가 정상적으로 Ollama와 통신하고 인덱스 로직을 처리하는지 단위 테스트로 확인합니다.

```bash
# 1. Ollama API 호출 테스트 (Mock 사용)
python3 tests/test_common.py

# 2. 인덱스 차원 변경 로직 테스트 (Mock 사용)
python3 tests/test_indexer.py
```
**성공 기준**: 두 테스트 모두 `OK`가 출력되어야 합니다.

### Step 2: 인덱스 자동 갱신 확인 (핵심)
기존에 384차원(Stub) 인덱스가 존재하거나 인덱스가 없는 상태에서, 애플리케이션이 768차원(Ollama) 인덱스를 올바르게 생성하는지 확인합니다.

1.  **Indexer 실행**
    ```bash
    python3 app/indexer.py
    ```
2.  **로그 확인**
    *   **케이스 A (최초 실행)**: `Creating index...` -> `Index created.`
    *   **케이스 B (기존 인덱스 존재 시)**: `Index exists with DIM 384, expected 768. Dropping index...` -> `Index created.`

**성공 기준**: 실행 로그에 에러 없이 인덱스가 생성되었다는 메시지가 표시되어야 합니다.

### Step 3: 데이터 적재 및 검색 품질 확인
실제 텍스트 데이터를 벡터화하여 저장하고, 검색이 되는지 확인합니다.

1.  **데이터 적재 (Ingest)**
    *   샘플 데이터를 Postgres에 넣고 Outbox 이벤트를 발행합니다.
    ```bash
    python3 app/ingest.py
    ```
    *   로그: `Upserted chunk ...` 메시지 확인.

2.  **Indexer가 데이터 처리 확인**
    *   앞서 실행해 둔 `app/indexer.py` 터미널을 확인합니다.
    *   로그: `Indexed chunk ...` 메시지가 실시간으로 올라오는지 확인합니다. 이때 실제 Ollama API를 호출하여 임베딩을 생성하므로 이전보다 속도가 약간 느릴 수 있습니다.

3.  **검색 수행 (Query)**
    ```bash
    python3 app/query.py
    ```
    *   사용자 입력을 받아 검색을 수행합니다.
    *   로그: 검색 결과 문서와 유사도 점수(Score)가 출력됩니다.

**성공 기준**: 검색 결과가 쿼리와 의미적으로 관련된 내용을 포함하고 있어야 합니다. (예: "Postgres" 검색 시 데이터베이스 관련 문서 반환)

---

## 3. 심화 검증: Valkey 상태 직접 확인
Valkey CLI를 사용하여 실제로 인덱스 차원이 변경되었는지 검증합니다.

```bash
# Valkey 컨테이너 내의 CLI 실행
docker exec -it rag-highperf-valkey valkey-cli

# 인덱스 정보 조회
127.0.0.1:6379> FT.INFO idx:chunks
```

**출력 결과 확인**:
응답 내용 중 `attributes` 섹션을 찾아 `vector` 필드의 `DIM` 값이 **768**인지 확인합니다.

```text
...
10) "attributes"
11) 1) "identifier"
    2) "vector"
    3) "attribute"
    4) "vector"
    5) "type"
    6) "VECTOR"
    7) "params"
    8)  1) "DIM"
        2) "768"  <-- 이 부분이 핵심
...
```

---

## 4. 트러블슈팅

*   **ConnectionRefusedError (Max retries exceeded)**:
    *   Ollama가 실행 중이지 않거나 포트(11434)가 차단되었는지 확인하세요.
    *   `curl http://localhost:11434` 명령어로 연결을 테스트해 보세요.

*   **ResponseError: Index already exists**:
    *   `indexer.py`의 자동 갱신 로직이 실패했을 수 있습니다. 수동으로 인덱스를 삭제해 보세요: `docker exec -it rag-highperf-valkey valkey-cli FT.DROPINDEX idx:chunks`.
