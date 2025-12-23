# Sprint 2 Plan: 시스템 스키마 비교 및 프로젝트 완료

## 1. 스프린트 정보 (Sprint Information)
- **스프린트 기간:** 2025년 12월 29일 ~ 2025년 12월 31일 (3일)
- **팀 Capacity:** 1.0 FTE

## 2. 스프린트 목표 (Sprint Goal)
> **새롭게 추가된 시스템 스키마 비교 요구사항을 구현하고, 전체 테스트 스위트를 안정화하여 프로젝트를 최종 완료한다.**

## 3. 스프린트 백로그 (Sprint Backlog)
이번 스프린트에서는 아래의 Story를 중점적으로 다룹니다.

| Epic | Story | Task | 상태 |
|---|---|---|---|
| **Epic 2: 테스트 개발** | **Story 2.5:** 시스템 스키마 변경 사항 검증 | **(Sys-Schema) Test:** `information_schema.tables` 목록 비교 | To-Do |
| | | **(Sys-Schema) Test:** `information_schema.columns` 목록 비교 | To-Do |
| | | **(Sys-Schema) Test:** `mysql` 데이터베이스의 주요 시스템 테이블 목록 비교 | To-Do |
| | **Story 2.6:** 전체 시스템 변수 비교 | **(Global-Vars) Test:** 각 버전에서 `SHOW GLOBAL VARIABLES` 전체 결과 수집 | Done |
| | | **(Global-Vars) Test:** 두 버전 간에 값이 다른 변수, 한쪽에만 존재하는 변수 목록화 | Done |
| | | **(Global-Vars) Test:** 비교 결과를 정량적으로 요약하여 리포트에 포함 | Done |

## 4. Definition of Done (DoD)
- **[Code]** 작성된 모든 코드는 `flake8` 또는 `black` 스타일 가이드를 준수한다.
- **[Test]** 개발된 `pytest` 코드는 `pytest` 명령어로 실행 시 에러 없이 동작해야 한다. (테스트 실패는 허용)
- **[Execution]** 개발된 테스트 스크립트는 두 MySQL 인스턴스에 모두 접속하여 쿼리를 실행하고 결과를 반환할 수 있어야 한다.
- **[Report]** 최종 실행 후 `mysql_version_diff_test_report.md` 보고서가 정상적으로 자동 생성되어야 한다.
- **[Commit]** 모든 작업은 `main` 브랜치에 병합 가능한 상태여야 한다.
