# MySQL 8.0.42 vs 8.4.7 비교 테스트베드 구축 및 테스트 자동화 요청

## 🎯 작업 목적 (Goal)

MySQL 8.0.42와 MySQL 8.4.7 간의 **기능/동작/기본 파라미터 차이점**을  
실제 실행 환경에서 **테스트로 검증**할 수 있는 실험 환경을 구축하고,  
Python 기반 테스트 스크립트를 통해 **차이를 재현·분석·정리**한다.

본 작업은 **DBaaS(Database as a Service) 제공팀의 사전 기술 검토**를 목적으로 하며,  
결과물은 내부 기술 검토 보고서 및 업그레이드 의사결정 자료로 활용된다.

---

## 🧱 실행 환경 제약 (Constraints)

- OS: **Windows + WSL2 (Ubuntu)**
- MySQL 실행 방식: **Docker Compose 기반**
- 테스트 자동화 언어: **Python**
- 테스트 프레임워크: `pytest` 기반
- 로컬 개발 환경에서 재현 가능해야 함
- 외부 상용 도구 사용 금지 (오픈소스/기본 패키지 위주)

---

## 🧩 전체 작업 범위 (Scope)

### 1️⃣ MySQL 실행 환경 구성
- Docker Compose로 **MySQL 8.0.42**와 **MySQL 8.4.7**을 동시에 실행
- 각 MySQL은 서로 다른 포트를 사용
- 초기화 SQL(init.sql) 및 설정 파일(my.cnf) 분리
- 기본 파라미터는 최대한 **각 버전의 default 동작을 유지**

### 2️⃣ 테스트 요구 사항 
아래 항목들을 **실제 테스트로 확인**할 수 있어야 함:

## (A) 스키마 / DDL 차이  
**(pytest 자동화 대상)**

### A-1. FK(Foreign Key) 제약 엄격성

#### 1) 부모 테이블에 PK / UNIQUE 제약이 없는 경우
- 부모 테이블에 PK 또는 UNIQUE 제약이 없는 상태에서 FK 생성 시도
- **기대 결과**
  - FK 생성 실패 또는 성공 여부 확인
  - 에러 코드 및 에러 메시지 비교

#### 2) 컬럼 타입 mismatch
- 예시:
  - `INT` ↔ `BIGINT`
  - `SIGNED` ↔ `UNSIGNED`
- **기대 결과**
  - FK 생성 성공/실패 여부
  - Warning 발생 여부 vs Error 발생 여부 구분

#### 3) 컬럼 length mismatch
- 예시:
  - `VARCHAR(191)` ↔ `VARCHAR(255)`
- **기대 결과**
  - FK 생성 성공/실패 여부
  - Warning / Error 구분

#### 4) Collation mismatch
- 예시:
  - `utf8mb4_general_ci` ↔ `utf8mb4_0900_ai_ci`
- **기대 결과**
  - FK 생성 성공/실패 여부
  - Warning / Error 구분

#### 5) FK 옵션 동작 (DDL 수용 여부)
- `ON DELETE CASCADE`
- `ON UPDATE CASCADE`
- **기대 결과**
  - FK 옵션 포함 DDL 수용 여부 비교

#### 검증 방법
- `information_schema.referential_constraints`
- `information_schema.key_column_usage`
- 위 메타데이터 조회를 통해 FK 실제 생성 여부 확인

---

### A-2. PK 없는 테이블 정책

#### 테스트 항목
1. PK 없는 InnoDB 테이블 생성 허용 여부
2. PK 없는 테이블에 Secondary Index 생성 가능 여부
3. PK 없는 테이블의 메타데이터 확인

#### 검증 방법
- `SHOW TABLE STATUS`
- `information_schema.tables`
- PK 존재 여부 및 테이블 속성 비교

---

### A-3. Collation / Character Set 조합에 따른 영향

#### 1) 서로 다른 collation 테이블 간 JOIN
- 서로 다른 collation을 가진 테이블 간 JOIN 쿼리 실행
- **기대 결과**
  - 에러 발생 여부
  - Warning 발생 여부

#### 2) 인덱스 생성 시 collation 영향
- 동일 컬럼에 대해 인덱스 생성 시도
- **기대 결과**
  - 인덱스 생성 성공 / 실패 여부

---

### A-4. 신규 예약어로 인한 DDL / SQL 오류

#### 테스트 방법
- 대상 MySQL 버전 기준 신규 예약어 후보 리스트(최소 10개) 준비
- 예약어를 다음 위치에 사용:
  - 테이블명
  - 컬럼명
- 백틱(`) 사용 전 / 후로 DDL 실행

#### 기대 결과
- DDL 성공 / 실패 여부 비교
- 에러 메시지 및 에러 코드 수집

> 참고  
> 예약어 리스트는 테스트 코드 내부에 **고정 리스트**로 포함하거나,  
> MySQL 버전별 분기 처리로 관리한다.

---

## (B) 인증 및 계정 플러그인 호환성  
**(pytest 자동화 대상)**

### B-1. 인증 플러그인 접속 가능 여부

#### 테스트 항목
1. `mysql_native_password`
   - 해당 인증 플러그인으로 계정 생성
   - Python 드라이버를 통한 접속 테스트
2. `caching_sha2_password`
   - 기본 인증 플러그인 계정 생성
   - Python 드라이버를 통한 접속 테스트

#### 검증 항목
- 접속 성공 여부
- 접속 실패 시 에러 코드 및 에러 메시지 기록
- `SHOW CREATE USER` 결과 기록

> 참고  
> TLS 설정을 포함한 복잡한 인증 시나리오는 환경 준비 부담으로 인해 본 테스트 범위에서 제외한다.

---

## (C) 기본 파라미터 차이  
**(pytest 자동화 대상)**

### C-1. 핵심 변수 덤프 및 diff

#### 수집 대상 변수
아래 변수는 `SHOW VARIABLES LIKE ...` 명령으로 수집하여 JSON 형태로 저장한다.

- `binlog_expire_logs_seconds`
- `innodb_flush_neighbors`
- `innodb_buffer_pool_in_core_file`
- `innodb_flush_log_at_trx_commit`
- `innodb_log_file_size`
- `gtid_mode`
- `enforce_gtid_consistency`
- `log_bin`
- `binlog_row_image`

#### 검증 항목
- 각 변수 값 수집 성공 여부
- 대상 간 변수 값 차이를 리포트에 포함

---

## (E) 간단 성능 비교  
**(pytest 자동화 대상 – 경향 관찰 목적)**

> 본 테스트의 목적은 절대 성능 비교가 아니라,  
> **상대적 성능 경향(trend)** 을 자동으로 수집하는 것이다.

---

### E-1. Insert TPS 테스트

#### 테스트 조건
- 단일 테이블
- PK: `AUTO_INCREMENT BIGINT`
- 간단한 payload 컬럼 구성
- Insert 건수:
  - N = 50,000 ~ 200,000 (테스트 환경에 따라 조절)

#### 수집 지표
- TPS (Transactions Per Second)
- 평균 latency (ms / operation)

---

### E-2. Select Latency 테스트

#### 테스트 항목
1. PK 기반 lookup
   - 10,000회 반복
2. Secondary Index 기반 lookup
   - 10,000회 반복

#### 수집 지표
- 평균 latency
- p95 latency
- p99 latency (가능한 범위 내)

---

### 공통 조건
- Warm-up 수행 (예: 5,000회)
- 각 테스트는 3~5회 반복 실행
- 최종 결과는 **중앙값(median)** 기준으로 기록


### 테스트 결과 정리 요구 사항 
pytest 실행 후 아래 산출물을 생성할 것:

1. test_results.json

- 케이스별:
  . name
  . sql
  . status(pass/fail)
  . error_code/error_message
  . warnings
  . verification_query_result(선택)

2. mysql_version_diff_test_report.md
- 주요 차이점 요약(표 포함)
- 실패 케이스 재현 SQL 포함
- “운영 영향(정성)” 한 줄 코멘트 포함


---

## 🗂️ 결과물 요구 사항 (Deliverables)

### 📁 디렉토리 구조
다음과 같은 프로젝트 구조를 생성할 것:

```
mysql-compare/
├── docker-compose.yml
├── mysql80/
│   ├── my.cnf
│   └── init.sql
├── mysql84/
│   ├── my.cnf
│   └── init.sql
└── python/
    ├── requirements.txt
    ├── config.py
    ├── common_db.py
    └── tests/
        ├── test_fk.py
        ├── test_schema_compat.py
        ├── test_auth.py
        ├── test_show_variables.py
        └── test_perf_simple.py
```

### 🐳 docker-compose
- MySQL 8.0.42, 8.4.7 컨테이너를 동시에 기동
- 포트 충돌 없이 접근 가능해야 함
- WSL 환경에서 바로 실행 가능해야 함

### 🐍 Python 테스트 코드
- 동일 테스트를 두 MySQL 버전에 반복 실행
- **에러 발생 여부, 동작 차이, 결과 값 차이**를 출력
- 처음에는 assert를 최소화하고 **관찰 가능한 로그 중심**
- pytest 실행 시 `-s` 옵션으로 결과 확인 가능

### 📊 테스트 출력 예시
- “8.0에서는 성공, 8.4에서는 실패”와 같은 패턴이 명확히 보이도록 로그 출력
- 기본 파라미터 값은 나란히 비교 출력

---

## 🧪 테스트 설계 원칙

- 테스트는 **차이를 드러내기 위한 실험**이지, 단순 성공 테스트가 아님
- 일부 테스트는 실패가 정상 (예: FK mismatch, native_password 로그인)
- DBaaS 관점에서 “위험 신호”를 포착할 수 있도록 구성
- 결과를 표/리스트로 정리하기 쉽게 출력

---

## 🧠 기대 활용 시나리오

- DBaaS 업그레이드 사전 기술 검토
- MySQL 8.4 도입 시 고객 영향 분석 근거
- 내부 업그레이드 가이드 / 체크리스트 작성
- 추후 MySQL 8.4.x → 차기 버전 테스트 자동화 기반

---

## 🧪 5️⃣ TDD 방식 개발 가이드

### 개발 가이드 문서
- 아래 경로의 가이드 문서 참조

/home/ubuntu/dev-proj/valkey_agile_test/docs/dev_guide.txt

## 📄 Agile 문서 세트

### docs/prd.md
- 프로젝트 개요, 목표, 사용자 시나리오, 기능 정의

### docs/backlog.md
- Epic/Story/Task 기반 정의

### docs/sprint_plan.md
- Sprint 1 기간, 목표, Capacity, Definition of Done 포함

### docs/progress.md
- 날짜 / 작업 / 테스트 결과 / 커버리지 정리

### docs/retro.md
- 잘된 점 / 개선점 / 다음 스프린트 액션 아이템

---

## 🚀 최종 요청

위 요구 사항을 충족하는:

1. Docker Compose 기반 MySQL 8.0.42 / 8.4.7 실행 환경
2. Python + pytest 기반 비교 테스트 스크립트
3. 실행 방법 및 테스트 목적이 명확한 코드

를 **실행 가능한 상태로** 작성해 달라.

각 파일은 **바로 복사해서 실행 가능한 수준**으로 작성할 것.

개발은 TDD 방식 개발 가이드 참조, 문서는 Agile 문서 세트 내용 참조해서 진행할 것. 
