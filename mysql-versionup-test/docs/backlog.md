# Backlog: MySQL 8.0 vs 8.4 비교 테스트 자동화

## Epic 1: MySQL 비교 테스트 환경 구축
> **Goal:** 두 MySQL 버전을 동시에 실행하고 테스트할 수 있는 안정적인 기반 환경을 구축합니다.

### Story 1.1: Docker Compose를 이용한 듀얼 MySQL 환경 구성
- **As a** DBaaS 엔지니어,
- **I want to** `docker-compose up` 명령 하나로 MySQL 8.0.42와 8.4.7을 동시에 실행할 수 있는 환경을 구성하여,
- **So that** 버전 간 비교 테스트를 쉽고 빠르게 시작할 수 있다.

#### Tasks
- [ ] `docker-compose.yml` 파일 작성 (MySQL 8.0.42, 8.4.7 서비스 정의)
- [ ] 각 서비스의 포트를 다르게 설정하여 포트 충돌 방지 (e.g., 33060, 33061)
- [ ] 각 버전에 맞는 `mysql/mysql-server` Docker 이미지 태그 명시
- [ ] 각 버전별 `my.cnf` 및 `init.sql`을 볼륨 마운트하여 설정을 분리
- [ ] 컨테이너 재시작 시에도 데이터가 유지되도록 `volume` 설정

---

## Epic 2: 비교 테스트 스크립트 개발
> **Goal:** Python과 pytest를 사용하여 두 버전 간의 주요 기능 차이를 자동으로 검증하고 재현합니다.

### Story 2.1: 스키마 및 DDL 동작 차이 검증
- **As a** DBaaS 엔지니어,
- **I want to** FK 제약, PK 없는 테이블, Collation, 예약어 등 DDL 관련 동작 차이를 검증하는 자동화된 테스트를 실행하여,
- **So that** 업그레이드 시 발생할 수 있는 스키마 관련 호환성 이슈를 사전에 식별할 수 있다.

#### Tasks
- [ ] **(FK) Test:** 부모 테이블 PK/Unique 제약 없는 경우 FK 생성 테스트
- [ ] **(FK) Test:** 컬럼 타입/길이/Collation 불일치 시 FK 생성 테스트
- [ ] **(Schema) Test:** PK 없는 테이블 생성 및 Secondary Index 생성 테스트
- [ ] **(Schema) Test:** 서로 다른 Collation을 가진 테이블 간 JOIN 테스트
- [ ] **(Schema) Test:** 신규 예약어를 테이블/컬럼명으로 사용 시 DDL 테스트

### Story 2.2: 인증 플러그인 호환성 검증
- **As a** DBaaS 엔지니어,
- **I want to** `mysql_native_password`와 `caching_sha2_password` 인증 방식의 계정으로 각 MySQL 버전에 접속하는 테스트를 자동화하여,
- **So that** 구형 드라이버나 클라이언트의 접속 가능 여부를 미리 확인할 수 있다.

#### Tasks
- [ ] **(Auth) Test:** `mysql_native_password` 사용 계정 생성 및 접속 테스트
- [ ] **(Auth) Test:** `caching_sha2_password` 사용 계정 생성 및 접속 테스트
- [ ] **(Auth) Test:** 접속 실패 시 에러 코드 및 메시지 기록

### Story 2.3: 기본 시스템 변수 비교
- **As a** DBaaS 엔지니어,
- **I want to** 지정된 주요 시스템 변수 목록을 두 버전에서 자동으로 추출하고 비교하여,
- **So that** 버전 간 기본 정책 변경 사항을 빠르게 파악할 수 있다.

#### Tasks
- [ ] **(Variables) Test:** `SHOW VARIABLES` 명령으로 주요 변수 값 수집
- [ ] **(Variables) Test:** 수집된 변수 값을 버전별로 비교하여 차이점 출력

### Story 2.4: 기본 성능 경향 비교
- **As a** DBaaS 엔지니어,
- **I want to** 간단한 Insert와 Select 쿼리의 성능(TPS, Latency)을 측정하는 테스트를 실행하여,
- **So that** 버전 간 성능 변화의 경향성을 파악하고 잠재적 성능 저하 리스크를 인지할 수 있다.

#### Tasks
- [ ] **(Perf) Test:** 대량 Insert 작업에 대한 TPS 측정
- [ ] **(Perf) Test:** PK 및 Secondary Index 기반 Select Latency 측정 (평균, p95)
- [ ] **(Perf) Test:** 테스트 전 Warm-up 로직 추가

### Story 2.5: 시스템 스키마 변경 사항 검증
- **As a** DBaaS 엔지니어,
- **I want to** `information_schema`와 `mysql` 데이터베이스의 테이블 및 컬럼 목록을 비교하는 테스트를 실행하여,
- **So that** 시스템 스키마의 변경, 추가, 또는 삭제된 항목을 식별하고 업그레이드 시 잠재적인 호환성 문제를 예측할 수 있다.

#### Tasks
- [ ] **(Sys-Schema) Test:** `information_schema.tables` 목록 비교
- [ ] **(Sys-Schema) Test:** `information_schema.columns` 목록 비교
- [ ] **(Sys-Schema) Test:** `mysql` 데이터베이스의 주요 시스템 테이블 목록 비교 (e.g., `user`, `db`)

### Story 2.6: 전체 시스템 변수 비교
- **As a** DBaaS 엔지니어,
- **I want to** 두 MySQL 버전의 `SHOW GLOBAL VARIABLES` 결과를 전체 비교하여,
- **So that** 사전에 정의되지 않은 파라미터의 변경 사항까지 모두 식별하고 잠재적 영향을 분석할 수 있다.

#### Tasks
- [ ] **(Global-Vars) Test:** 각 버전에서 `SHOW GLOBAL VARIABLES` 전체 결과 수집
- [ ] **(Global-Vars) Test:** 두 버전 간에 값이 다른 변수, 한쪽에만 존재하는 변수 목록화
- [ ] **(Global-Vars) Test:** 비교 결과를 정량적으로 요약하여 리포트에 포함

---

## Epic 3: 테스트 결과 리포팅
> **Goal:** 테스트 결과를 사람이 쉽게 이해할 수 있는 형태로 가공하고 요약하여 빠른 의사결정을 지원합니다.

### Story 3.1: 자동화된 테스트 결과 리포트 생성
- **As a** 기술 의사결정권자,
- **I want to** `pytest` 실행 후 자동으로 생성된 요약 보고서를 통해,
- **So that** 버전 간 핵심 차이점과 운영 영향도를 신속하게 파악하고 업그레이드 여부를 결정할 수 있다.

#### Tasks
- [ ] **(Report) Task:** `pytest` 테스트 결과를 `test_results.json` 파일로 저장하는 로직 구현
- [ ] **(Report) Task:** JSON 결과를 바탕으로 `mysql_version_diff_test_report.md` 마크다운 보고서 자동 생성
- [ ] **(Report) Task:** 보고서에 버전별 테스트 결과 비교 테이블, 실패 케이스 상세 정보, 운영 영향도 코멘트 포함

### Story 3.2: 통합 리포트 생성
- **As a** 기술 의사결정권자,
- **I want to** Standalone 및 InnoDB Cluster 테스트 결과를 모두 포함한 통합 리포트를 통해,
- **So that** 전체적인 버전 간 차이점과 클러스터 환경에서의 영향도를 한 번에 파악할 수 있다.

#### Tasks
- [ ] **(Report) Task:** `mysql_version_diff_test_new_report.md` 파일 생성 로직 구현
- [ ] **(Report) Task:** Standalone 테스트 결과와 Cluster 비교 결과를 통합하여 기술
- [ ] **(Report) Task:** Version-driven Diff와 Cluster-driven Diff를 명확히 구분하여 표시

---

## Epic 4: InnoDB Cluster 비교 테스트
> **Goal:** InnoDB Cluster 환경에서 Primary 노드의 설정을 비교하여 클러스터 환경 특화된 차이점을 식별합니다.

### Story 4.1: InnoDB Cluster 환경 구성
- **As a** DBaaS 엔지니어,
- **I want to** Docker Compose를 사용하여 3-node InnoDB Cluster와 MySQL Router를 포함한 환경을 자동으로 구성하여,
- **So that** 복잡한 클러스터 설정 없이도 즉시 비교 테스트를 수행할 수 있다.

#### Tasks
- [ ] **(Cluster) Task:** MySQL 8.0.42용 3-node Cluster + Router `docker-compose` 구성
- [ ] **(Cluster) Task:** MySQL 8.4.7용 3-node Cluster + Router `docker-compose` 구성
- [ ] **(Cluster) Task:** MySQL Shell을 이용한 클러스터 부트스트랩 자동화 스크립트 작성

### Story 4.2: Primary Node Global Variables 비교
- **As a** DBaaS 엔지니어,
- **I want to** Primary 노드를 자동으로 식별하고 해당 노드의 Global Variables를 수집/비교하여,
- **So that** 클러스터 환경에서만 발생하는 파라미터 변경 사항(Cluster-driven Diff)을 파악할 수 있다.

#### Tasks
- [ ] **(Cluster) Task:** Cluster 상태 조회를 통한 Primary 노드 식별 로직 구현
- [ ] **(Cluster) Task:** Primary 노드 대상 `SHOW GLOBAL VARIABLES` 수집
- [ ] **(Cluster) Task:** Version-driven Diff와 Cluster-driven Diff 분류 로직 구현

