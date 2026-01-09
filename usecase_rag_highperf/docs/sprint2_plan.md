# Sprint 2 Plan: Ollama 임베딩 연동

## 1. 스프린트 개요
*   **목표**: 기존의 Stub(가짜) 임베딩을 제거하고, 로컬 Ollama 환경(`nomic-embed-text`)을 연동하여 실제 의미 기반 검색(Semantic Search)이 가능한 RAG 시스템으로 고도화한다.
*   **기간**: 1주 (예상)
*   **참여자**: 개발자 1명 (AI Assistant 포함)

## 2. 스프린트 목표 (Sprint Goal)
1.  Ollama API 연동을 위한 환경 설정(`OLLAMA_BASE_URL`)을 완료한다.
2.  애플리케이션(`common.py`)에서 실제 임베딩 모델(768 dim)을 호출하도록 변경한다.
3.  변경된 임베딩 차원에 맞춰 기존 데이터(Postgres, Valkey)와의 호환성을 확인하거나 재색인(Re-indexing)을 수행한다.

## 3. 대상 백로그 아이템 (Selected Backlog Items)

### Epic 1: 인프라 및 환경 구성
*   **INFRA-003**: Ollama 환경 변수 추가 (`.env.example` 업데이트)

### Epic 3: 애플리케이션 개발
*   **APP-006**: Ollama 임베딩 연동
    *   `requirements.txt`: `requests` 추가
    *   `common.py`: `EMBED_DIM` 768로 변경, `embed_text_ollama` 구현

## 4. 완료 조건 (Definition of Done)
*   `.env` 파일에 `OLLAMA_BASE_URL`이 설정되어야 한다.
*   `ingest.py` 실행 시 Ollama를 통해 768차원의 벡터가 생성되어야 한다.
*   `indexer.py`가 768차원 벡터를 Valkey에 정상적으로 색인해야 한다 (기존 인덱스 호환성 고려).
*   `query.py` 실행 시 실제 의미적으로 유사한 문서가 검색되어야 한다.

## 5. 일일 계획 (Rough Schedule)
*   **Day 1**: 환경 변수 설정 (INFRA-003) 및 공통 모듈 수정 (APP-006)
*   **Day 2**: Ingest/Indexer/Query 서비스 연동 테스트 및 디버깅
*   **Day 3**: 전체 End-to-End 테스트 및 문서 업데이트

## 6. 주의사항 (Risks & Mitigation)
*   **인덱스 호환성**: 기존 Valkey 인덱스는 384차원이므로, 768차원으로 변경 시 인덱스를 재생성(`FT.DROPINDEX`)해야 함.
*   **Ollama 연결**: 로컬 Ollama 서비스가 실행 중이어야 하며, `nomic-embed-text` 모델이 pull 되어 있어야 함.
