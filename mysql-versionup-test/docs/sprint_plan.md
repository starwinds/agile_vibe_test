# Sprint 1 Plan: MySQL 비교 테스트 환경 구축 및 핵심 기능 검증

## 1. 스프린트 정보 (Sprint Information)
- **스프린트 기간:** 2025년 12월 22일 ~ 2025년 12월 26일 (5일)
- **팀 Capacity:** 1.0 FTE

## 2. 스프린트 목표 (Sprint Goal)
> **MySQL 8.0과 8.4를 동시에 실행할 수 있는 Docker 기반 테스트 환경을 구축하고, 업그레이드 시 가장 영향도가 클 것으로 예상되는 Foreign Key 제약 및 인증 방식의 차이를 검증하는 자동화된 테스트 코드를 개발하여 실행 가능한 초기 버전을 확보한다.**

## 3. 스프린트 백로그 (Sprint Backlog)
이번 스프린트에서는 아래의 Story들을 중점적으로 다룹니다.

| Epic | Story | Task | 상태 |
|---|---|---|---|
| **Epic 1: 환경 구축** | **Story 1.1:** 듀얼 MySQL 환경 구성 | `docker-compose.yml` 작성 | To-Do |
| | | 각 버전별 `my.cnf`, `init.sql` 구성 | To-Do |
| | | 프로젝트 디렉토리 구조 생성 | To-Do |
| **Epic 2: 테스트 개발** | **Story 2.1:** 스키마/DDL 차이 검증 | **(FK) Test:** 부모 테이블 PK/Unique 제약 없는 경우 FK 생성 | To-Do |
| | | **(FK) Test:** 컬럼 타입/길이/Collation 불일치 시 FK 생성 | To-Do |
| | **Story 2.2:** 인증 플러그인 호환성 검증 | **(Auth) Test:** `mysql_native_password` 계정 접속 테스트 | To-Do |
| | | **(Auth) Test:** `caching_sha2_password` 계정 접속 테스트 | To-Do |
| | | Python 프로젝트 설정 (`requirements.txt`, `config.py`) | To-Do |

## 4. Definition of Done (DoD)
- **[Code]** 작성된 모든 코드는 `flake8` 또는 `black` 스타일 가이드를 준수한다.
- **[Test]** 개발된 `pytest` 코드는 `pytest` 명령어로 실행 시 에러 없이 동작해야 한다. (테스트 실패는 허용)
- **[Environment]** `docker-compose up -d` 명령이 성공적으로 실행되며, 두 MySQL 컨테이너가 정상 기동해야 한다.
- **[Execution]** 개발된 테스트 스크립트는 두 MySQL 인스턴스에 모두 접속하여 쿼리를 실행하고 결과를 반환할 수 있어야 한다.
- **[Documentation]** 코드 내에 개발 의도를 파악할 수 있는 최소한의 주석이나 타입 힌트가 포함되어야 한다.
- **[Merge]** 모든 작업은 `main` 브랜치에 병합 가능한 상태여야 한다. (PR, Code Review는 생략)
