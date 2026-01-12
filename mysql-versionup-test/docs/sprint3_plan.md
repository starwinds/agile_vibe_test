# Sprint 3 Plan: InnoDB Cluster 비교 및 통합 리포트

## 1. 스프린트 정보 (Sprint Information)
- **스프린트 기간:** 2026년 1월 13일 ~ 2026년 1월 15일 (3일)
- **팀 Capacity:** 1.0 FTE

## 2. 스프린트 목표 (Sprint Goal)
> **InnoDB Cluster 환경(Primary-only)에서의 MySQL 8.0 vs 8.4 비교 테스트를 구현하고, Standalone 및 Cluster 결과를 통합한 새로운 리포트를 생성한다.**

## 3. 스프린트 백로그 (Sprint Backlog)
이번 스프린트에서는 아래의 Epic과 Story를 중점적으로 다룹니다.

| Epic | Story | Task | 상태 |
|---|---|---|---|
| **Epic 4: InnoDB Cluster 비교 테스트** | **Story 4.1:** InnoDB Cluster 환경 구성 | **(Cluster) Task:** MySQL 8.0.42용 3-node Cluster + Router `docker-compose` 구성 | To-Do |
| | | **(Cluster) Task:** MySQL 8.4.7용 3-node Cluster + Router `docker-compose` 구성 | To-Do |
| | | **(Cluster) Task:** MySQL Shell을 이용한 클러스터 부트스트랩 자동화 스크립트 작성 | To-Do |
| | **Story 4.2:** Primary Node Global Variables 비교 | **(Cluster) Task:** Cluster 상태 조회를 통한 Primary 노드 식별 로직 구현 | To-Do |
| | | **(Cluster) Task:** Primary 노드 대상 `SHOW GLOBAL VARIABLES` 수집 | To-Do |
| | | **(Cluster) Task:** Version-driven Diff와 Cluster-driven Diff 분류 로직 구현 | To-Do |
| **Epic 3: 테스트 결과 리포팅** | **Story 3.2:** 통합 리포트 생성 | **(Report) Task:** `mysql_version_diff_test_new_report.md` 파일 생성 로직 구현 | To-Do |
| | | **(Report) Task:** Standalone 테스트 결과와 Cluster 비교 결과를 통합하여 기술 | To-Do |
| | | **(Report) Task:** Version-driven Diff와 Cluster-driven Diff를 명확히 구분하여 표시 | To-Do |

## 4. Definition of Done (DoD)
- **[Code]** 작성된 모든 코드는 `flake8` 또는 `black` 스타일 가이드를 준수한다.
- **[Test]** 개발된 `pytest` 코드는 `pytest` 명령어로 실행 시 에러 없이 동작해야 한다.
- **[Execution]** `docker-compose`를 통해 InnoDB Cluster가 정상적으로 구성되고, Primary 노드 식별 및 변수 수집이 자동화되어야 한다.
- **[Report]** 최종 실행 후 `mysql_version_diff_test_new_report.md` 통합 보고서가 정상적으로 자동 생성되어야 한다.
- **[Commit]** 모든 작업은 `main` 브랜치에 병합 가능한 상태여야 한다.
