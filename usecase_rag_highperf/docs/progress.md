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
| VER-001 | End-to-End 테스트 | 🏃 | Query 결과 확인 필요 |
| VER-002 | README 작성 | ✅ | README.md 생성 완료 |

## 이슈 및 특이사항
*   Indexer가 백그라운드 실행 시 로그 출력이 지연되는 현상이 있었으나, 사용자가 직접 실행하여 3개 청크 색인 성공 확인.
*   현재 Valkey와 Postgres 간 데이터 동기화 완료 상태.
