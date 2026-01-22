# Sprint 4 Retrospective: Demo App & Pattern B

## 1. 개요 (Overview)
*   **기간**: 2026-01-22 ~ 2026-01-28
*   **목표**: End-user가 체감할 수 있는 검색 데모 애플리케이션(FastAPI + Streamlit) 개발 및 Pattern B (Postgres SoR) 구조 도입.
*   **참여자**: Gemini Agent

## 2. 달성한 목표 (Achievements)

### 2.1 Demo App (FastAPI + Streamlit) 완성
*   **FastAPI Backend**: Semantic, Keyword, Hybrid 검색 엔드포인트를 제공하는 API 서버를 구축했습니다. `pydantic` 스키마를 통해 API 입출력을 명확히 정의했습니다.
*   **Streamlit Frontend**: 사용자가 직관적으로 검색 품질을 테스트할 수 있는 UI를 구현했습니다. Preset 버튼, 검색 모드 설정, 결과 내 본문 표시, 디버그 모드 등 사용자 편의 기능을 포함했습니다.
*   **End-to-End 연동**: Streamlit UI에서 FastAPI 백엔드를 호출하고, 백엔드는 Valkey/Postgres를 조회하는 전체 파이프라인이 정상 동작함을 확인했습니다.

### 2.2 Pattern B (Postgres SoR) 도입
*   **Data Durability**: 임베딩 벡터와 메타데이터의 원본(Source of Record)으로 Postgres `chunk_embeddings` 테이블을 도입하여, Valkey가 재시작되거나 데이터가 유실되어도 복구 가능한 구조를 마련했습니다.
*   **Dual Engine Support**: Demo API 및 UI에서 검색 엔진으로 `valkey` 외에 `pgvector`를 선택하거나, Valkey 장애 시 Fallback 할 수 있는 기능을 구현했습니다.
*   **Rebuild Tool**: Postgres 데이터를 기반으로 Valkey 인덱스를 고속으로 재구축하는 `rebuild_valkey_from_pg.py` 도구를 개발했습니다.

### 2.3 데이터 생성 고도화
*   **Real Data**: `Faker` 기반의 무의미한 텍스트 대신, HuggingFace `datasets` (Wikipedia 등)를 연동하여 실제 문맥을 가진 고품질 테스트 데이터를 생성할 수 있게 되었습니다.
*   **Multilingual**: 한국어(`ko`) 데이터 생성 지원을 추가하여 다국어 검색 테스트 기반을 마련했습니다.
*   **Performance**: `COPY` 명령을 사용한 Bulk Insert 최적화를 통해 대량 데이터 생성 속도를 개선했습니다.

## 3. 잘된 점 (What went well)
*   **검증 중심 개발**: 각 기능 구현 후 `manual_test_sprint4_guide.md`에 따른 체계적인 검증을 수행하여 버그를 조기에 발견하고 수정했습니다.
*   **확장성 있는 구조**: `Indexer`와 `Demo API`가 `valkey`와 `pgvector`를 유연하게 오갈 수 있도록 설계되어 향후 엔진 비교나 하이브리드 전략 고도화가 용이해졌습니다.
*   **시각화**: Streamlit을 통한 시각화는 검색 품질(랭킹, 스코어 등)을 직관적으로 파악하는 데 큰 도움이 되었습니다.

## 4. 아쉬운 점 및 개선할 점 (What could be improved)
*   **Valkey Module 호환성**: 개발 과정에서 Valkey 컨테이너의 모듈 로딩 설정 확인이 필요했습니다. (현재는 정상 동작)
*   **테스트 자동화**: E2E 테스트가 수동 가이드에 의존하고 있습니다. 향후 `playwright` 등을 활용한 UI 테스트나 API 통합 테스트 자동화가 고려되어야 합니다.
*   **Hybrid 튜닝**: 현재 단순 가중치 합(Weighted Sum) 방식을 사용하고 있어, 점수 분포가 다른 두 검색 결과(Keyword, Vector)의 결합이 최적화되지 않았을 수 있습니다. RRF(Reciprocal Rank Fusion) 도입이 필요합니다.

## 5. 다음 스프린트 제안 (Action Items for Next Sprint)
*   **Hybrid Search 고도화**: RRF 알고리즘 구현 및 비교.
*   **Postgres Full-Text Search**: `tsvector` 기반의 더 강력한 키워드 검색 도입.
*   **Metadata Filtering**: 검색 시 메타데이터 필터링 기능 추가.
*   **Benchmark**: 대규모 데이터셋에 대한 성능 벤치마크 수행.

## 6. 추가 고도화 아이디어 (Future Enhancements)
*   **RAG Chat Interface**: 단순 검색 결과 나열을 넘어, 검색된 문서를 Context로 하여 LLM(Ollama)이 답변을 생성하는 대화형 인터페이스(Chat UI) 도입.
*   **Vector Visualization**: 쿼리와 검색 결과의 벡터 공간상 위치를 2D/3D로 시각화(PCA/t-SNE)하여 Semantic Search의 원리를 시각적으로 설명.
*   **Real-time Ingestion**: Streamlit UI에서 사용자가 직접 문서를 업로드하고, 즉시 인덱싱되어 검색 가능한 상태가 되는 과정을 시연 (Pipeline 속도 검증).
*   **Relevance Feedback**: 검색 결과에 대한 사용자 피드백(좋아요/싫어요)을 수집하여 향후 검색 랭킹 튜닝이나 모델 파인튜닝에 활용할 수 있는 기반 마련.
