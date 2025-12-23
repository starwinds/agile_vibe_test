# MySQL 8.0.42 vs 8.4.7 비교 테스트 보고서

> [!NOTE]
> **보고서 생성일:** 2025-12-23 10:51:43
> 본 보고서는 MySQL 8.0(LTS 이전 마지막 마이너)과 8.4(LTS) 버전 간의 기능적 차이와 성능 경향성을 분석한 결과입니다.

---

## 1. 테스트 결과 요약

| 분류 | 결과 | 비고 |
| :--- | :--- | :--- |
| **전체 테스트 수** | **36** | |
| **성공 (Passed)** | <span style="color:green">**29**</span> | |
| **실패 (Failed)** | <span style="color:red">**7**</span> | 하단 상세 분석 참조 |
| **실행 시간** | 14.43초 | |

---

## 2. 주요 차이점 및 실패 항목 분석

실패한 7개의 항목은 크게 **인증 방식의 변화**, **시스템 변수 기본값 변경**, **시스템 스키마 구조 변경**으로 분류됩니다.

### 2.1. 인증 (Authentication) 관련 실패
MySQL 8.4에서는 보안 강화를 위해 일부 레거시 인증 방식이나 드라이버 호환성에서 차이가 발생했습니다.

> [!WARNING]
> **mysql.connector 및 pymysql 드라이버 호환성 이슈**
> - `native_user`, `sha2_user` 모두 8.4 환경에서 인증 실패 발생.
> - **원인:** 8.4에서 기본 인증 플러그인 정책 변화 및 드라이버의 `cryptography` 패키지 의존성 문제.

| 테스트 케이스 | 상세 에러 메시지 |
| :--- | :--- |
| `mysql.connector-native_user` | `Access denied for user 'native_user'@'_gateway' (using password: YES)` |
| `mysql.connector-sha2_user` | `Access denied for user 'sha2_user'@'_gateway' (using password: YES)` |
| `pymysql-native_user` | `'cryptography' package is required for sha256_password or caching_sha2_password` |
| `pymysql-sha2_user` | `'cryptography' package is required for sha256_password or caching_sha2_password` |

### 2.2. 시스템 변수 및 스키마 차이

| 분류 | 테스트 항목 | 차이점 상세 |
| :--- | :--- | :--- |
| **시스템 변수** | `innodb_buffer_pool_in_core_file` | 8.0: `ON` → 8.4: `OFF` (기본값 변경) |
| **시스템 스키마** | `information_schema.tables` | 8.4에서 `TABLESPACES` 테이블 제거됨 |
| **시스템 스키마** | `information_schema.columns` | `TABLESPACES` 관련 컬럼 9개 제거됨 |

---

## 3. 성능 테스트 결과 (경향성)

MySQL 8.4.7은 8.0.42 대비 전반적으로 소폭 향상된 성능을 보여줍니다.

| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 변화율 |
| :--- | :--- | :--- | :--- |
| **Insert TPS** (높을수록 좋음) | 154,925.49 | 157,251.29 | <span style="color:green">**+1.50%** ↑</span> |
| **Select Latency** (ms) | 0.4107 | 0.3979 | <span style="color:green">**-3.13%** ↓</span> |

---

## 4. 전체 시스템 변수 비교 (Global Variables)

### 4.1. 변수 통계 요약

| 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 차이 |
| :--- | :--- | :--- | :--- |
| **전체 변수 수** | 631 | 622 | -9 |
| **8.0 전용 변수** | 15 | - | 제거됨 |
| **8.4 전용 변수** | - | 6 | 신규 추가 |
| **값이 다른 변수** | 28 | 28 | 기본값 변경 등 |

### 4.2. 값이 다른 변수 상세 (총 28개)

> [!TIP]
> 가독성을 위해 28개의 변수를 **성능/InnoDB**, **시스템 경로/빌드**, **기타 설정**으로 분류하여 정리했습니다.

#### A. 성능 및 InnoDB 관련 변수 (핵심 변경 사항)
8.4 버전에서 고성능 환경 최적화를 위해 기본값이 상향 조정된 항목들입니다.

| 변수명 | MySQL 8.0.42 | MySQL 8.4.7 | 비고 |
| :--- | :--- | :--- | :--- |
| `innodb_io_capacity` | 200 | **10000** | 대폭 상향 |
| `innodb_io_capacity_max` | 2000 | **20000** | 대폭 상향 |
| `innodb_log_buffer_size` | 16777216 (16MB) | **67108864 (64MB)** | 4배 증가 |
| `innodb_flush_method` | `fsync` | `O_DIRECT` | 기본값 변경 |
| `innodb_read_io_threads` | 4 | 11 | |
| `innodb_doublewrite_pages` | 4 | 128 | |
| `innodb_adaptive_hash_index` | `ON` | `OFF` | |
| `innodb_change_buffering` | `all` | `none` | |
| `innodb_use_fdatasync` | `OFF` | `ON` | |
| `temptable_max_mmap` | 1073741824 | 0 | |
| `temptable_use_mmap` | `ON` | `OFF` | |

#### B. 시스템 경로, 빌드 및 버전 정보
환경 차이나 빌드 시점에 따라 달라지는 정보성 변수들입니다.

| 변수명 | MySQL 8.0.42 | MySQL 8.4.7 |
| :--- | :--- | :--- |
| `innodb_version` | 8.0.42 | 8.4.7 |
| `build_id` | cd3aff82... | dfd0d55f... |
| `character_sets_dir` | /usr/share/mysql-8.0/charsets/ | /usr/share/mysql-8.4/charsets/ |
| `lc_messages_dir` | /usr/share/mysql-8.0/ | /usr/share/mysql-8.4/ |
| `general_log_file` | /var/lib/mysql/51a1645acb81.log | /var/lib/mysql/042757887f10.log |
| `pid_file` | /var/lib/mysql/51a1645acb81.pid | /var/lib/mysql/042757887f10.pid |
| `relay_log` | 51a1645acb81-relay-bin | 042757887f10-relay-bin |
| `relay_log_basename` | /var/lib/mysql/51a1645acb81-relay-bin | /var/lib/mysql/042757887f10-relay-bin |
| `relay_log_index` | /var/lib/mysql/51a1645acb81-relay-bin.index | /var/lib/mysql/042757887f10-relay-bin.index |
| `slow_query_log_file` | /var/lib/mysql/51a1645acb81-slow.log | /var/lib/mysql/042757887f10-slow.log |

#### C. 기타 설정 및 모니터링 변수
복제 일관성, 옵티마이저 스위치 및 Performance Schema 관련 변경 사항입니다.

| 변수명 | MySQL 8.0.42 | MySQL 8.4.7 |
| :--- | :--- | :--- |
| `group_replication_consistency` | `EVENTUAL` | `BEFORE_ON_PRIMARY_FAILOVER` |
| `optimizer_switch` | (기존 설정) | (기존) + `hash_set_operations=on` |
| `performance_schema_error_size` | 5319 | 5550 |
| `performance_schema_max_memory_classes` | 450 | 470 |
| `performance_schema_max_rwlock_classes` | 60 | 100 |
| `performance_schema_max_statement_classes` | 219 | 220 |
| `innodb_buffer_pool_in_core_file` | `ON` | `OFF` |

### 4.3. MySQL 8.4.7 신규 추가 변수
- `explain_json_format_version`
- `performance_schema_max_meter_classes`
- `performance_schema_max_metric_classes`
- `restrict_fk_on_non_standard_key`
- `set_operations_buffer_size`
- `tls_certificates_enforced_validation`

### 4.4. MySQL 8.4.7에서 제거된 변수 (8.0에만 존재)
- `avoid_temporal_upgrade`, `binlog_transaction_dependency_tracking`, `default_authentication_plugin`, `expire_logs_days`, `have_openssl`, `have_ssl`, `log_bin_use_v1_row_events`, `master_info_repository`, `new`, `old`, `relay_log_info_file`, `relay_log_info_repository`, `show_old_temporals`, `slave_rows_search_algorithms`, `transaction_write_set_extraction`