# Sprint 1 Retrospective: RAG High-Perf MVP

## 1. 개요
*   **기간**: Sprint 1 (MVP 구축)
*   **목표**: Postgres(SoR) + Valkey(Vector) 기반의 고성능 RAG 시스템 기본 골격 완성 및 End-to-End 검증.

## 2. 성과 (What Went Well)
*   **인프라 구축 완료**: Docker Compose를 통해 Postgres 16.9와 Valkey 환경을 신속하게 구성하고 연동에 성공함.
*   **핵심 파이프라인 구현**: 문서 적재(Ingest) -> 이벤트 발행(Outbox) -> 비동기 색인(Indexer) -> 검색(Query)으로 이어지는 RAG의 핵심 흐름을 모두 구현함.
*   **Transactional Outbox 패턴 적용**: Postgres 트랜잭션을 활용하여 데이터 정합성을 보장하면서도 비동기 처리가 가능한 구조를 확립함.
*   **ACL 기반 보안 검색**: 검색 결과에 대해 사용자 권한(ACL)을 필터링하는 로직을 초기 단계부터 반영하여 보안성을 고려함.
*   **Gemini CLI 활용**: PRD부터 코드 구현까지 Gemini CLI를 활용하여 개발 생산성을 극대화함.

## 3. 아쉬운 점 & 개선 포인트 (What Could Be Improved)
*   **Stub 임베딩 사용**: 현재는 `embed_text_stub` 함수로 가짜 임베딩을 생성하고 있어 실제 의미 기반 검색 품질을 평가할 수 없음.
*   **단순한 청킹 전략**: 고정 길이와 오버랩만 지원하는 단순한 청킹 방식을 사용 중임. 문서 구조(Markdown 헤더 등)를 고려한 지능형 청킹 필요.
*   **에러 처리 미흡**: Indexer가 이벤트 처리 중 실패했을 때의 재시도(Retry) 로직이나 Dead Letter Queue(DLQ) 처리가 부족함.
*   **테스트 커버리지**: End-to-End 검증은 되었으나, 각 모듈별 단위 테스트(Unit Test)가 부재함.
*   **하드코딩된 설정**: 일부 설정값이나 쿼리 파라미터가 코드 내에 하드코딩되어 있어 유연성이 떨어질 수 있음.

## 4. 향후 계획 (Action Items)
1.  **실제 임베딩 모델 연동**: OpenAI API 또는 HuggingFace 로컬 모델을 연동하여 `embed_text_stub` 대체.
2.  **고급 청킹 도입**: LangChain 등의 라이브러리를 활용하거나 커스텀 로직을 개선하여 의미 단위 청킹 구현.
3.  **Indexer 안정성 강화**: 예외 발생 시 재시도 로직 추가 및 실패 로그 기록 강화.
4.  **API 서버화**: 현재 CLI 형태의 실행 방식을 FastAPI 등을 활용한 REST API 서버로 전환하여 외부 연동성 확보.
5.  **모니터링 구성**: Prometheus/Grafana 등을 연동하여 처리량 및 지연 시간 모니터링 체계 구축.
