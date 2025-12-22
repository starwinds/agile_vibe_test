# MySQL 8.0.42 vs 8.4.7 비교 테스트 자동화 보고서
**보고서 생성일:** 2025-12-22 12:25:12

## 1. 테스트 요약
- **전체 테스트:** 36
- **성공:** 29
- **실패:** 7
- **실행 시간:** 14.43초

## 2. 주요 차이점 분석 (실패 항목)

| 테스트 분류 | 상세 내용 |
|---|---|
| **인증 (Authentication)** | `test_authentication_comparison[mysql.connector-native_user]`<br>**Failed: Authentication behavior differs for native_user with mysql.connector: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'native_user' with driver 'mysql.connector' ---
Failed to connect to mysql84 using mysql.connector with user native_user: 1045 (28000): Access denied for user 'native_user'@'_gateway' (using password: YES)
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **인증 (Authentication)** | `test_authentication_comparison[mysql.connector-sha2_user]`<br>**Failed: Authentication behavior differs for sha2_user with mysql.connector: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'sha2_user' with driver 'mysql.connector' ---
Failed to connect to mysql84 using mysql.connector with user sha2_user: 1045 (28000): Access denied for user 'sha2_user'@'_gateway' (using password: YES)
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **인증 (Authentication)** | `test_authentication_comparison[pymysql-native_user]`<br>**Failed: Authentication behavior differs for native_user with pymysql: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'native_user' with driver 'pymysql' ---
Failed to connect to mysql84 using pymysql with user native_user: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **인증 (Authentication)** | `test_authentication_comparison[pymysql-sha2_user]`<br>**Failed: Authentication behavior differs for sha2_user with pymysql: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'sha2_user' with driver 'pymysql' ---
Failed to connect to mysql84 using pymysql with user sha2_user: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **시스템 변수 (System Variable)** | `test_variable_comparison[innodb_buffer_pool_in_core_file]`<br>**AssertionError: Variable 'innodb_buffer_pool_in_core_file' differs: 8.0 is 'ON', 8.4 is 'OFF'
assert 'ON' == 'OFF'
  
  - OFF
  + ON**

**Test Output:**
```
--- Comparing variable: innodb_buffer_pool_in_core_file ---
[mysql80] innodb_buffer_pool_in_core_file = ON
[mysql84] innodb_buffer_pool_in_core_file = OFF
``` |
| **시스템 스키마 (System Schema)** | `test_information_schema_table_diff`<br>**AssertionError: information_schema.tables differ between versions.
assert (not set() and not {'TABLESPACES'})**

**Test Output:**
```
--- Comparing information_schema.tables ---
Tables removed in 8.4 (were in 8.0): ['TABLESPACES']
``` |
| **시스템 스키마 (System Schema)** | `test_information_schema_column_diff`<br>**AssertionError: information_schema.columns differ between versions.
assert (not set() and not {('TABLESPACES', 'AUTOEXTEND_SIZE'), ('TABLESPACES', 'ENGINE'), ('TABLESPACES', 'EXTENT_SIZE'), ('TABLESPACES', 'LOGFILE_GROUP_NAME'), ('TABLESPACES', 'MAXIMUM_SIZE'), ('TABLESPACES', 'NODEGROUP_ID'), ...})**

**Test Output:**
```
--- Comparing information_schema.columns ---
Columns removed in 8.4 (were in 8.0): [('TABLESPACES', 'AUTOEXTEND_SIZE'), ('TABLESPACES', 'ENGINE'), ('TABLESPACES', 'EXTENT_SIZE'), ('TABLESPACES', 'LOGFILE_GROUP_NAME'), ('TABLESPACES', 'MAXIMUM_SIZE'), ('TABLESPACES', 'NODEGROUP_ID'), ('TABLESPACES', 'TABLESPACE_COMMENT'), ('TABLESPACES', 'TABLESPACE_NAME'), ('TABLESPACES', 'TABLESPACE_TYPE')]
``` |

## 3. 성능 테스트 결과 (경향성)

| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 비교 |
|---|---|---|---|
| Insert TPS (높을수록 좋음) | 154,925.49 | 157,251.29 | **+1.50%** |
| Select Latency (ms) (낮을수록 좋음) | 0.4107 | 0.3979 | **-3.13%** |