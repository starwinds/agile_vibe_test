# Sprint 2 Retrospective: 시스템 스키마 비교 및 프로젝트 완료

## 1. 스프린트 개요
- **기간:** 2025년 12월 29일 ~ 2025년 12월 31일
- **목표:** 시스템 스키마(information_schema, mysql DB) 비교 구현 및 전체 테스트 스위트 안정화

## 2. 목표 달성 현황 (Sprint Goal Achievement)

| Story | Task | 상태 | 비고 |
|---|---|---|---|
| **Story 2.5: 시스템 스키마 변경 사항 검증** | `information_schema.tables` 목록 비교 | **Done** | `test_system_schema.py`에 구현 완료 |
| | `information_schema.columns` 목록 비교 | **Done** | `test_system_schema.py`에 구현 완료 |
| | `mysql` DB 주요 테이블 목록 비교 | **Done** | `test_system_schema.py`에 구현 완료 |
| **Story 2.6: 전체 시스템 변수 비교** | `SHOW GLOBAL VARIABLES` 결과 수집 | **Done** | `test_show_variables.py`에 구현 완료 |
| | 변수 차이점(값 변경, 추가/삭제) 목록화 | **Done** | `variable_comparison.json`으로 관리 |
| | 리포트 자동 생성 및 요약 포함 | **Done** | `generate_report.py`를 통해 자동화 완료 |

## 3. 주요 성과 (Key Achievements)

### 3.1. 시스템 스키마 변화 포착
- MySQL 8.4에서 `information_schema.TABLESPACES` 테이블이 삭제된 것을 확인하였습니다.
- 관련 컬럼들(`AUTOEXTEND_SIZE`, `ENGINE` 등)이 함께 제거된 것을 자동으로 검증하였습니다.

### 3.2. 시스템 변수 정밀 분석
- 총 600여 개의 시스템 변수를 전수 비교하여, 값이 변경된 28개의 변수와 8.4에서 추가/삭제된 변수들을 명확히 식별하였습니다.
- 특히 `innodb_buffer_pool_in_core_file` 등 주요 InnoDB 관련 변수의 기본값 변화를 확인하였습니다.

### 3.3. 테스트 및 리포트 자동화 완료
- `pytest`와 `pytest-json-report`를 결합하여 테스트 결과를 구조화된 데이터로 수집하고, 이를 바탕으로 가독성 높은 마크다운 보고서(`mysql_version_diff_test_report.md`)를 자동 생성하는 파이프라인을 구축하였습니다.

## 4. Lesson Learned & 개선 필요 사항

### 4.1. 잘된 점 (Keep)
- **Agile 방식의 접근:** Sprint 단위로 목표를 설정하고, PRD/Backlog/Plan 문서를 통해 체계적으로 관리한 점이 프로젝트 완수에 큰 도움이 되었습니다.
- **자동화의 힘:** 수동으로 비교하기 힘든 수백 개의 변수와 스키마 정보를 코드로 검증함으로써 정확도를 높였습니다.

### 4.2. 아쉬운 점 (Problem)
- **문서 업데이트 지연:** 실제 구현은 완료되었으나 `sprint2_plan.md`의 상태(To-Do)가 제때 업데이트되지 않아 혼선이 있을 수 있었습니다.
- **성능 테스트의 변동성:** 테스트 환경에 따라 성능 지표가 민감하게 변하는 경향이 있어, 보다 안정적인 벤치마크 환경 구축이 필요함을 느꼈습니다.

### 4.3. 향후 과제 (Try)
- **회귀 테스트 강화:** 업그레이드 후 실제 애플리케이션 쿼리 레벨에서의 호환성 테스트를 추가할 수 있습니다.
- **CI/CD 통합:** 새로운 MySQL 마이너 버전이 출시될 때마다 자동으로 비교 테스트가 실행되도록 GitHub Actions 등에 통합하는 것을 고려할 수 있습니다.

## 5. 최종 결론
Sprint 2를 통해 계획했던 모든 기술적 검증 항목이 성공적으로 구현되었으며, MySQL 8.0에서 8.4로의 전환 시 주의해야 할 핵심 변경 사항(인증, 스키마, 변수)을 명확히 정리하였습니다. 본 프로젝트를 통해 확보된 테스트 자산은 향후 실제 운영 환경의 업그레이드 작업 시 중요한 가이드라인이 될 것입니다.
