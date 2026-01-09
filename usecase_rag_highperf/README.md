# RAG High-Perf MVP (Postgres + Valkey)

이 프로젝트는 Postgres(Source of Record)와 Valkey(Vector Search)를 연동한 고성능 RAG 시스템의 MVP 구현체입니다. Transactional Outbox 패턴을 사용하여 데이터 정합성을 보장하며, ACL(Access Control List)을 통한 권한 기반 검색을 지원합니다.

## 1. 시스템 아키텍처
1.  **Ingest**: Postgres에 문서, 청크, ACL 정보를 저장하고 `outbox_events`를 생성합니다.
2.  **Indexer**: Outbox 이벤트를 폴링하여 텍스트 임베딩을 생성하고 Valkey에 벡터 색인을 수행합니다.
3.  **Query**: Valkey에서 KNN 검색을 수행한 후, Postgres의 ACL 정보를 참조하여 최종 결과를 필터링합니다.

## 2. 사전 준비
*   Docker & Docker Compose
*   Python 3.10+
*   Ollama (Local) - `nomic-embed-text` 모델 필요 (`ollama pull nomic-embed-text`)

## 3. 시작하기

### 3.1 환경 설정
```bash
cd usecase_rag_highperf
cp .env.example .env
# .env 파일 내의 접속 정보 확인 및 수정
# OLLAMA_BASE_URL (기본: http://localhost:11434) 설정
```

### 3.2 인프라 구동
```bash
docker compose up -d
```

### 3.3 의존성 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

## 4. 실행 순서

### 4.1 상태 점검
```bash
python app/healthcheck.py
```

### 4.2 데이터 적재 (Ingest)
```bash
python app/ingest.py
```

### 4.3 색인 (Indexer)
이 프로세스는 계속 실행되어 이벤트를 처리합니다.
```bash
python app/indexer.py
```

### 4.4 검색 (Query)
```bash
python app/query.py
```

### 3.4 Ollama 상태 점검
최근 업데이트된 `app/check_ollama.py` 스크립트를 통해 Ollama 서비스와 `nomic-embed-text` 모델 존재 여부를 확인할 수 있습니다.
```bash
python app/check_ollama.py
```

## 5. 프로젝트 구조
*   `app/`: Python 애플리케이션 소스 코드
    *   `check_ollama.py`: Ollama 연동 확인 유틸리티
*   `docs/`: 문서 및 분석 결과
    *   `retro2.md`: Sprint 2(Ollama 연동) 회고록
*   `postgres/`: DB 스키마 및 초기화 스크립트
*   `docker-compose.yml`: 인프라 설정 파일
