# MySQL 8.0.42 vs 8.4.7 비교 테스트 자동화 보고서
**보고서 생성일:** 2025-12-22 11:13:47

## 1. 테스트 요약
- **전체 테스트:** 36
- **성공:** 29
- **실패:** 7
- **실행 시간:** 14.43초

## 2. 주요 차이점 분석 (실패 항목)

| 테스트 분류 | 내용 |
|---|---|

| **인증 (Authentication)** | `test_authentication_comparison[mysql.connector-native_user]`<br>Failed: Authentication behavior differs for native_user with mysql.connector: 8.0 is SUCCESS, 8.4 is FAIL |
| **인증 (Authentication)** | `test_authentication_comparison[mysql.connector-sha2_user]`<br>Failed: Authentication behavior differs for sha2_user with mysql.connector: 8.0 is SUCCESS, 8.4 is FAIL |
| **인증 (Authentication)** | `test_authentication_comparison[pymysql-native_user]`<br>Failed: Authentication behavior differs for native_user with pymysql: 8.0 is SUCCESS, 8.4 is FAIL |
| **인증 (Authentication)** | `test_authentication_comparison[pymysql-sha2_user]`<br>Failed: Authentication behavior differs for sha2_user with pymysql: 8.0 is SUCCESS, 8.4 is FAIL |
| **시스템 변수 (System Variable)** | `test_variable_comparison[innodb_buffer_pool_in_core_file]`<br>AssertionError: Variable 'innodb_buffer_pool_in_core_file' differs: 8.0 is 'ON', 8.4 is 'OFF'
assert 'ON' == 'OFF'
  
  - OFF
  + ON |
| **알 수 없음** | `test_information_schema_table_diff`<br>AssertionError: information_schema.tables differ between versions.
assert (not set() and not {'TABLESPACES'}) |
| **알 수 없음** | `test_information_schema_column_diff`<br>AssertionError: information_schema.columns differ between versions.
assert (not set() and not {('TABLESPACES', 'AUTOEXTEND_SIZE'), ('TABLESPACES', 'ENGINE'), ('TABLESPACES', 'EXTENT_SIZE'), ('TABLESPACES', 'LOGFILE_GROUP_NAME'), ('TABLESPACES', 'MAXIMUM_SIZE'), ('TABLESPACES', 'NODEGROUP_ID'), ...}) |

## 3. 성능 테스트 결과 (경향성)

| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 비교 |
|---|---|---|---|

| Insert TPS (높을수록 좋음) | 154,925.49 | 157,251.29 | **+1.50%** |
| Select Latency (ms) (낮을수록 좋음) | 0.4107 | 0.3979 | **-3.13%** |