# 스프린트 계획 (Sprint 1)

## 1. 스프린트 정보

- **스프린트 기간:** 2025년 11월 19일 ~ 2025년 11월 26일 (1주)
- **스프린트 목표:** Redis/Valkey 호환성 테스트를 위한 기본 환경 구축 및 핵심 CRUD 시나리오 실행 자동화
- **담당 팀/인원:** Gemini CLI (1명)

## 2. 스프린트 목표 (Sprint Goal)

> 이번 스프린트에서는 사용자가 Docker를 통해 Redis와 Valkey를 실행하고, 단일 Python 스크립트로 기본적인 CRUD 및 데이터 구조 테스트를 수행하여 그 결과를 테이블 형태로 비교할 수 있는 최소 기능 제품(MVP)을 개발한다.

## 3. Capacity 계획

- **총 개발 시간:** 5일 (주말 제외)
- **집중률:** 100%
- **총 Capacity:** 1.0 Person-Days/Day * 5 days = 5 PD

## 4. 스프린트 백로그 (Sprint Backlog)

| Epic | 사용자 스토리 | Task | 담당자 | 예상 시간 (PD) |
|---|---|---|---|---|
| **환경 구축** | 1.1: DB 실행 | Task 1.1.1: `docker-compose.yml` 작성 | Gemini | 0.5 |
| | | Task 1.1.3: README 문서화 | Gemini | (통합) |
| | 1.2: 라이브러리 설치 | Task 1.2.1: `requirements.txt` 생성 | Gemini | 0.2 |
| **핵심 기능** | 2.1: CRUD 검증 | Task 2.1.1: `basic_crud.py` 구현 | Gemini | 1.0 |
| | 2.2: 데이터 구조 검증 | Task 2.2.1: `data_structures.py` 구현 | Gemini | 1.0 |
| **자동화** | 3.1: 테스트 실행 | Task 3.1.1: `test_runner.py` 기본 구조 | Gemini | 1.5 |
| | | Task 3.1.3: `config.py` 구현 | Gemini | (통합) |
| | | Task 3.1.4: 결과 테이블 출력 | Gemini | (통합) |
| **문서화** | 3.3: 사용법 문서화 | Task 3.3.1: `README.md` 초안 작성 | Gemini | 0.5 |
| | | Task 3.3.2: 실행 방법 명시 | Gemini | (통합) |
| **총합** | | | | **4.7 PD** |

## 5. 완료의 정의 (Definition of Done - DoD)

- 모든 코드는 `test_runner.py`를 통해 오류 없이 실행되어야 한다.
- `basic_crud`와 `data_structures` 시나리오가 성공적으로 실행되고 결과가 출력되어야 한다.
- `docker-compose up -d`로 데이터베이스 환경이 정상적으로 구성되어야 한다.
- `README.md`에 명시된 절차에 따라 사용자가 테스트를 재현할 수 있어야 한다.
- 모든 작업은 현재 브랜치에 커밋되어야 한다.
