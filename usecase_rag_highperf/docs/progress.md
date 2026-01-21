# Project Progress: RAG High-Perf

## Sprint 1: MVP 구축 (진행중)

| ID | Task | Status | Note |
|:---|:---|:---:|:---|
| INFRA-001 | Docker Compose 구성 | ✅ | Postgres, Valkey 구동 완료 |
| INFRA-002 | 환경 변수 설정 | ✅ | .env 설정 완료 |
| DB-001 | 스키마 및 확장 스크립트 | ✅ | pgvector, tables 생성 완료 |
| APP-001 | 공통 모듈 및 의존성 | ✅ | common.py, requirements.txt |
| APP-002 | Ingest 서비스 구현 | ✅ | doc_1 적재 완료 |
| APP-003 | Indexer 서비스 구현 | ✅ | 3개 청크 색인 완료 |
| APP-004 | Query 서비스 구현 | 🏃 | 최종 검증 대기 중 |
| APP-005 | Healthcheck 구현 | ✅ | 정상 동작 확인 |
| VER-001 | End-to-End 테스트 | ✅ | Query 결과 확인 완료 (Ollama 연동) |
| VER-002 | README 작성 | ✅ | README.md 생성 완료 |

## Sprint 4: Demo App & Pattern B (완료)

| ID | Task | Status | Note |
|:---|:---|:---:|:---|
| DEMO-001 | 프로젝트 구조 및 의존성 | ✅ | app/demo_api, app/streamlit_app, requirements-demo.txt |
| DEMO-002 | Demo API 구현 | ✅ | Semantic(Vector), Keyword(ILIKE), Hybrid 검색 구현 |
| DEMO-003 | Streamlit UI 구현 | ✅ | 검색 모드, 프리셋, 디버그 모드 UI |
| DEMO-004 | 문서화 | ✅ | manual_test_sprint4_guide.md 작성 |
| DEMO-005 | 검색 결과 표시 개선 | ✅ | 본문(Snippet/Content) 및 메타데이터 표시 개선 |
| DEMO-006 | Backend - Schema Update | ✅ | chunk_embeddings 테이블 추가 (SoR) |
| DEMO-007 | Backend - Indexer Update | ✅ | Dual Write (PG & Valkey) 구현 |
| DEMO-008 | Backend - Rebuild Tool | ✅ | Postgres 데이터 기반 Valkey 복구 도구 구현 |
| DEMO-009 | Demo API - Engine Support | ✅ | Engine 선택 (Valkey/PGVector/Fallback) 및 PGVector 검색 구현 |
| DEMO-010 | Streamlit UI - Engine Selector | ✅ | UI에 엔진 선택 옵션 및 Source 표시 기능 추가 |
| ADV-008 | HuggingFace Datasets 연동 | ✅ | wikitext 데이터셋 활용 |
| ADV-009 | 데이터 샘플링 및 전처리 | ✅ | 실제 문맥 데이터 추출 및 정제 로직 구현 |
| ADV-010 | 데이터 생성기 고도화 | ✅ | generate_dataset.py 실제 데이터 기반으로 고도화 완료 |
| ADV-011 | 데이터 품질 및 성능 검증 | ✅ | 실제 문맥 유지 및 적재 확인 완료 |

## 이슈 및 특이사항
*   **Valkey Search 모듈의 Full-Text Search(TEXT 타입) 미지원 이슈**
    *   **현상**: `indexer.py`에서 `chunk_text` 필드를 `TEXT` 타입으로 인덱싱 시도 시 `Unknown argument TEXT` 에러 발생. `valkey-cli`를 통한 직접 생성 시에도 동일한 에러 발생 확인.
    *   **원인 분석**: 현재 `valkey/valkey-bundle:latest` 이미지에 포함된 `search` 모듈(ver 1.0.0)이 `VECTOR`와 `TAG` 타입은 지원하지만, 형태소 분석 및 자연어 검색을 위한 `TEXT` 타입은 아직 구현되지 않았거나 비활성화된 상태임.
    *   **조치 사항**: 
        1.  데모 앱의 키워드 검색 기능을 정상화하기 위해, Valkey 대신 Postgres의 `ILIKE` 연산자를 사용하는 방식으로 검색 엔진을 긴급 전환함.
        2.  결과적으로 데모 앱은 **Semantic 검색은 Valkey(Vector)**, **Keyword 검색은 Postgres(Text)**를 사용하는 하이브리드 엔진 구조로 동작함.
    *   **향후 과제**: 보다 강력한 키워드 검색(BM25, 랭킹 등)이 필요한 경우 Postgres의 Full-Text Search(`tsvector`)를 정식 도입하거나, `TEXT` 타입을 지원하는 Valkey Search 모듈 버전으로 업그레이드 검토 필요.
*   **PGVector 타입 에러**: `psycopg`와 `pgvector` 연동 시 `operator does not exist` 에러 발생.
    *   조치: Python 리스트를 문자열(`str(list)`)로 변환 후 `%s::vector` 명시적 캐스팅을 통해 해결.

## Sprint 2: Ollama 연동 (완료)

| ID | Task | Status | Note |
|:---|:---|:---:|:---|
| INFRA-003 | Ollama 환경 변수 추가 | ✅ | .env.example 업데이트 |
| APP-006 | Ollama 임베딩 연동 | ✅ | common.py 수정 (Stub -> Ollama) |
| TEST-001 | 단위 테스트 추가 | ✅ | tests/test_common.py, tests/test_indexer.py |
| DOC-001 | 수동 테스트 가이드 | ✅ | manual_test_guide.md 작성 |
| FIX-001 | 인덱스 차원 자동 갱신 버그 수정 | ✅ | FT.INFO 'dimensions' 키 처리 |

## 이슈 및 특이사항
*   Indexer가 백그라운드 실행 시 로그 출력이 지연되는 현상이 있었으나, 사용자가 직접 실행하여 3개 청크 색인 성공 확인.
*   현재 Valkey와 Postgres 간 데이터 동기화 완료 상태.
*   Sprint 2에서 Ollama(nomic-embed-text) 연동 완료 및 인덱스 768차원 자동 변환 기능 안정화.
