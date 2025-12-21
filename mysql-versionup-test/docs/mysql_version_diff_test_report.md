# MySQL 8.0.42 vs 8.4.7 비교 테스트 자동화 보고서
**보고서 생성일:** 2025-12-21 20:38:06

## 1. 테스트 요약
- **전체 테스트:** 33
- **성공:** 28
- **실패:** 5
- **실행 시간:** 22.72초

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

## 3. 성능 테스트 결과 (경향성)

| 측정 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 비교 |
|---|---|---|---|

| Insert TPS (높을수록 좋음) | 99,470.95 | 86,255.98 | **-13.29%** |
| Select Latency (ms) (낮을수록 좋음) | 0.6621 | 0.6764 | **+2.16%** |