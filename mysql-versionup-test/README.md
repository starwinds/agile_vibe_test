# MySQL 8.0 vs 8.4 버전 업그레이드 호환성 테스트 자동화

이 프로젝트는 MySQL 8.0.42 버전에서 8.4.7 LTS 버전으로 업그레이드 시 발생할 수 있는 호환성 이슈, 시스템 설정 변화, 그리고 성능 경향을 자동으로 검증하기 위한 테스트베드입니다.

## 🚀 프로젝트 개요

MySQL 8.4는 혁신 릴리스(Innovation Release) 이후의 첫 번째 LTS 버전으로, 여러 기본 설정과 인증 방식이 변경되었습니다. 본 프로젝트는 이러한 변화가 실제 운영 환경에 미칠 영향을 사전에 파악하기 위해 **Docker 기반의 독립된 테스트 환경**과 **Python/pytest 기반의 자동화된 검증 스위트**를 제공합니다.

## 🏗️ 프로젝트 구조

```text
mysql-versionup-test/
├── docs/                   # 프로젝트 문서 (PRD, 백로그, 리포트, 회고 등)
├── mysql-compare/          # 인프라 구성
│   ├── docker-compose.yml         # Standalone MySQL 정의
│   ├── docker-compose.cluster.yml # InnoDB Cluster (3-node) 정의
│   ├── mysql80/                   # 8.0용 설정
│   └── mysql84/                   # 8.4용 설정
└── python/                 # 테스트 자동화 스크립트
    ├── tests/              # pytest 기반 테스트 케이스
    ├── common_db.py        # DB 연결 및 유틸리티
    ├── run_tests.py        # 전체 테스트 실행기
    ├── compare_variables.py # Standalone 변수 비교 도구
    ├── generate_new_report.py # 통합 리포트 생성기 (Standalone + Cluster)
    └── generate_report.py  # 기존 Standalone 리포트 생성기
```

## 🧪 주요 테스트 항목

1.  **인증 방식 (Authentication)**
    - `mysql_native_password` 비활성화에 따른 접속 실패 검증
    - `caching_sha2_password` 및 `sha2_user` 호환성 확인
2.  **스키마 및 DDL 호환성 (Schema/DDL)**
    - Foreign Key 제약 조건 생성 규칙 변화 검증
    - PK 없는 테이블 생성 및 인덱스 정책 확인
    - 신규 예약어 및 Collation JOIN 호환성 테스트
3.  **시스템 스키마 (System Schema)**
    - `information_schema` 및 `mysql` DB의 테이블/컬럼 변경 사항 전수 비교
4.  **시스템 변수 (Global Variables)**
    - 600여 개의 시스템 변수 전수 비교 (기본값 변경, 추가/삭제 항목 식별)
5.  **성능 경향 (Performance)**
    - 버전 간 Insert TPS 및 Select Latency 상대적 비교
6.  **InnoDB Cluster 비교**
    - Cluster 환경에서의 Primary 노드 설정 차이 식별 (Version-driven vs Cluster-driven)

## 🛠️ 실행 방법

상세한 실행 가이드는 아래 문서를 참조하십시오.
- **[Standalone 테스트 가이드](./docs/manual_test_guide.md)**
- **[InnoDB Cluster 테스트 가이드](./docs/manual_test_cluster_guide.md)**

### 테스트 실행 및 통합 리포트 생성
```bash
# 1. Standalone 변수 수집
python compare_variables.py

# 2. Cluster 변수 수집 (Cluster 환경 구동 후)
pytest tests/test_cluster_variables.py

# 3. 통합 마크다운 리포트 생성
python generate_new_report.py
```

## 📊 테스트 결과 확인

테스트가 완료되면 아래 파일들을 통해 상세 결과를 확인할 수 있습니다.
- **통합 요약 보고서 (권장):** [docs/mysql_version_diff_test_new_report.md](./docs/mysql_version_diff_test_new_report.md)
- **Standalone 보고서:** [docs/mysql_version_diff_test_report.md](./docs/mysql_version_diff_test_report.md)

## 📝 프로젝트 현황

- **Sprint 1:** 인프라 구축, 인증 및 기본 스키마 테스트 완료
- **Sprint 2:** 시스템 스키마 및 전체 변수 비교, 리포트 자동화 완료
- **Sprint 3:** InnoDB Cluster 비교 및 통합 리포트(Version/Cluster 분류) 구현 완료
- **최종 회고:** [docs/retro2.md](./docs/retro2.md)
