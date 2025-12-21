# Progress: MySQL 8.0 vs 8.4 비교 테스트

## Sprint 1 (2025.12.22 ~ 2025.12.26)

---
### **Day 1: 2025-12-22**

**오늘의 목표:**
- 프로젝트 요구사항 분석 및 Agile 문서 세트 작성

**작업 내용:**
- `gemini_mysql_8_0_42_vs_8_4_7_test_prompt.md` 요구사항 분석 완료
- `docs/prd.md` 작성 완료
- `docs/backlog.md` 작성 완료 (Epic, Story, Task 정의)
- `docs/sprint_plan.md` 작성 완료 (Sprint 1 목표 및 범위 설정)
- `docs/progress.md` 생성 및 초기 작업 내용 기록

**Blocker / 이슈:**
- 없음

**테스트 결과:**
- N/A

---
### **Day 2: 2025-12-23**

**오늘의 목표:**
- 테스트 환경 구축 및 핵심 기능(인증, FK) 테스트 초안 구현

**작업 내용:**
- `docker-compose.yml` 및 `my.cnf`, `init.sql` 파일 작성 완료.
- Python 테스트 프로젝트 구조 생성 (`requirements.txt`, `config.py`, `common_db.py`).
- `pytest` `conftest.py` fixture 설정.
- `test_auth.py` 구현 및 실행.
- `test_fk.py` 일부 구현 및 실행.

**Blocker / 이슈:**
- **Docker 이미지 오류:** 초기 `mysql/mysql-server` 이미지 이름이 잘못되어 `docker pull`에 실패함. `mysql`로 변경하여 해결.
- **Python 경로 문제:** `pytest` 실행 시 모듈을 찾지 못하는 문제가 발생하여, `PYTHONPATH`를 설정하여 해결.

**테스트 결과:**
- `test_auth`: MySQL 8.4에서 인증 실패 확인 (의도된 결과).
- `test_fk`: 버전 간 오류 메시지 차이 확인.

---
### **Day 3: 2025-12-24**

**오늘의 목표:**
- 스키마 관련 테스트 전체 완료

**작업 내용:**
- `test_fk.py`에 컬럼 길이, Collation 불일치 테스트 추가 완료.
- `test_schema_compat.py`에 PK 없는 테이블, Collation JOIN, 예약어 테스트 구현 완료.
- 예약어 및 Collation 테스트의 예상 결과가 잘못되어, 여러 번의 디버깅을 통해 테스트 로직 수정 완료.

**Blocker / 이슈:**
- **테스트 로직 오류:** 예약어, Collation 테스트 등에서 DDL의 성공/실패 예측이 빗나가 여러 차례 코드를 수정함.
- **단순 오타:** `lower()` 메소드 호출 시 발생한 오타로 인해 불필요한 테스트 실패 및 디버깅 시간 소요.

**테스트 결과:**
- `test_fk`, `test_schema_compat`의 모든 테스트가 예상대로 동작함을 확인. 버전 간 동작이 동일하거나, 다른 경우 모두 성공적으로 포착함.

---
### **Day 4: 2025-12-25**

**오늘의 목표:**
- 시스템 변수, 성능 테스트 구현 및 보고서 자동화

**작업 내용:**
- `test_show_variables.py` 구현 및 `innodb_buffer_pool_in_core_file` 변수의 기본값 차이 발견.
- `test_perf_simple.py` 초안 구현 후, 비효율적인 Insert 로직을 `executemany`를 사용하도록 최적화.
- `pytest-json-report` 플러그인 추가.
- `generate_report.py` 스크립트 작성하여 `test_results.json` 기반으로 `md` 보고서 자동 생성.

**Blocker / 이슈:**
- **성능 테스트 지연:** 초기 성능 테스트가 매우 느려 사용자 요청으로 중단 후, 코드 최적화 진행.
- **보고서 생성 오류:** `pytest-json-report`의 출력 포맷에 대한 이해 부족으로 `KeyError`가 여러 번 발생. JSON 구조를 직접 확인하며 디버깅하여 해결.

**테스트 결과:**
- 모든 테스트가 실행되고, `mysql_version_diff_test_report.md`가 자동으로 생성됨을 확인.
- **성능:** 현재 테스트 환경에서는 MySQL 8.4가 8.0 대비 Insert TPS는 약 13% 저하, Select Latency는 약 2% 증가하는 경향을 보임.
- **변수:** `innodb_buffer_pool_in_core_file` 기본값이 `ON`에서 `OFF`로 변경됨.
- **인증:** 8.4에서 보안이 강화되어 기존 방식으로는 접속이 실패함.