# MySQL 8.0.42 vs 8.4.7 비교 테스트 자동화 보고서
**보고서 생성일:** 2025-12-24 10:17:31

## 1. 테스트 요약
- **전체 테스트:** 37
- **성공:** 31
- **실패:** 6
- **실행 시간:** 13.41초

## 2. 주요 차이점 분석 (실패 항목)

| 테스트 분류 | 상세 내용 |
|---|---|
| **인증 (Authentication)** | `test_authentication_comparison[mysql.connector-native_user]`<br>**Failed: Authentication behavior differs for native_user with mysql.connector: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'native_user' with driver 'mysql.connector' ---
Failed to connect to mysql84 using mysql.connector with user native_user: 1524 (HY000): Plugin 'mysql_native_password' is not loaded
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **인증 (Authentication)** | `test_authentication_comparison[pymysql-native_user]`<br>**Failed: Authentication behavior differs for native_user with pymysql: 8.0 is SUCCESS, 8.4 is FAIL**

**Test Output:**
```
--- Comparing auth for user 'native_user' with driver 'pymysql' ---
Failed to connect to mysql84 using pymysql with user native_user: (1524, "Plugin 'mysql_native_password' is not loaded")
Result for MySQL 8.0: SUCCESS
Result for MySQL 8.4: FAIL
``` |
| **시스템 변수 (System Variable)** | `test_variable_comparison[innodb_buffer_pool_in_core_file]`<br>**AssertionError: Variable 'innodb_buffer_pool_in_core_file' differs: 8.0 is 'ON', 8.4 is 'OFF'
assert 'ON' == 'OFF'
  
  [0m[91m- OFF[39;49;00m[90m[39;49;00m
  [92m+ ON[39;49;00m[90m[39;49;00m**

**Test Output:**
```
--- Comparing variable: innodb_buffer_pool_in_core_file ---
[mysql80] innodb_buffer_pool_in_core_file = ON
[mysql84] innodb_buffer_pool_in_core_file = OFF
``` |
| **시스템 변수 (System Variable)** | `test_global_variables_comparison`<br>**Failed: Differences found in global variables. See stdout for details.**

**Test Output:**
```
--- Comparing ALL global variables ---

### Variables with Different Values:
| Variable Name | MySQL 8.0 Value | MySQL 8.4 Value |
|---------------|-----------------|-----------------|
| `build_id` | `cd3aff82d0fd9b8a7b130b0b45cb5fdf7e2f29cf` | `dfd0d55f42f50a10cda6fd9baa83690e88c2511a` |
| `character_sets_dir` | `/usr/share/mysql-8.0/charsets/` | `/usr/share/mysql-8.4/charsets/` |
| `general_log_file` | `/var/lib/mysql/6a507411ba98.log` | `/var/lib/mysql/16e49a77b6ce.log` |
| `group_replication_consistency` | `EVENTUAL` | `BEFORE_ON_PRIMARY_FAILOVER` |
| `hostname` | `6a507411ba98` | `16e49a77b6ce` |
| `innodb_adaptive_hash_index` | `ON` | `OFF` |
| `innodb_buffer_pool_in_core_file` | `ON` | `OFF` |
| `innodb_change_buffering` | `all` | `none` |
| `innodb_doublewrite_pages` | `4` | `128` |
| `innodb_flush_method` | `fsync` | `O_DIRECT` |
| `innodb_io_capacity` | `200` | `10000` |
| `innodb_io_capacity_max` | `2000` | `20000` |
| `innodb_log_buffer_size` | `16777216` | `67108864` |
| `innodb_read_io_threads` | `4` | `11` |
| `innodb_use_fdatasync` | `OFF` | `ON` |
| `innodb_version` | `8.0.42` | `8.4.7` |
| `lc_messages_dir` | `/usr/share/mysql-8.0/` | `/usr/share/mysql-8.4/` |
| `optimizer_switch` | `index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on` | `index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on,hash_set_operations=on` |
| `performance_schema_error_size` | `5319` | `5550` |
| `performance_schema_max_memory_classes` | `450` | `470` |
| `performance_schema_max_rwlock_classes` | `60` | `100` |
| `performance_schema_max_statement_classes` | `219` | `220` |
| `pid_file` | `/var/lib/mysql/6a507411ba98.pid` | `/var/lib/mysql/16e49a77b6ce.pid` |
| `pseudo_thread_id` | `29` | `35` |
| `relay_log` | `6a507411ba98-relay-bin` | `16e49a77b6ce-relay-bin` |
| `relay_log_basename` | `/var/lib/mysql/6a507411ba98-relay-bin` | `/var/lib/mysql/16e49a77b6ce-relay-bin` |
| `relay_log_index` | `/var/lib/mysql/6a507411ba98-relay-bin.index` | `/var/lib/mysql/16e49a77b6ce-relay-bin.index` |
| `server_uuid` | `603891b5-dca7-11f0-8343-5a559a7196f3` | `605126eb-dca7-11f0-8f34-06c1c19faa35` |
| `slow_query_log_file` | `/var/lib/mysql/6a507411ba98-slow.log` | `/var/lib/mysql/16e49a77b6ce-slow.log` |
| `statement_id` | `22287` | `22407` |
| `temptable_max_mmap` | `1073741824` | `0` |
| `temptable_use_mmap` | `ON` | `OFF` |
| `timestamp` | `1766538819.299395` | `1766538819.326936` |
| `version` | `8.0.42` | `8.4.7` |

### Variables Unique to MySQL 8.0:
| Variable Name | MySQL 8.0 Value |
|---------------|-----------------|
| `avoid_temporal_upgrade` | `OFF` |
| `binlog_transaction_dependency_tracking` | `COMMIT_ORDER` |
| `default_authentication_plugin` | `mysql_native_password` |
| `expire_logs_days` | `0` |
| `have_openssl` | `YES` |
| `have_ssl` | `YES` |
| `log_bin_use_v1_row_events` | `OFF` |
| `master_info_repository` | `TABLE` |
| `new` | `OFF` |
| `old` | `OFF` |
| `relay_log_info_file` | `relay-log.info` |
| `relay_log_info_repository` | `TABLE` |
| `show_old_temporals` | `OFF` |
| `slave_rows_search_algorithms` | `INDEX_SCAN,HASH_SCAN` |
| `transaction_write_set_extraction` | `XXHASH64` |

### Variables Unique to MySQL 8.4:
| Variable Name | MySQL 8.4 Value |
|---------------|-----------------|
| `explain_json_format_version` | `1` |
| `performance_schema_max_meter_classes` | `30` |
| `performance_schema_max_metric_classes` | `600` |
| `restrict_fk_on_non_standard_key` | `ON` |
| `set_operations_buffer_size` | `262144` |
| `tls_certificates_enforced_validation` | `OFF` |
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
| Insert TPS (높을수록 좋음) | 156,575.62 | 162,460.73 | **+3.76%** |
| Select Latency (ms) (낮을수록 좋음) | 0.3777 | 0.3720 | **-1.49%** |

## 4. 전체 시스템 변수 비교 (Global Variables Comparison)

### 4.1. 요약

| 항목 | MySQL 8.0.42 | MySQL 8.4.7 | 차이 |
|---|---|---|---|
| 전체 변수 수 | 631 | 622 | -9:+ |
| 8.0에만 존재 | 15 | - | - |
| 8.4에만 존재 | - | 6 | - |
| 값이 다른 변수 | 28 | 28 | - |

### 4.2. 값이 다른 변수

| 변수명 | MySQL 8.0.42 | MySQL 8.4.7 |
|---|---|---|
| `build_id` | cd3aff82d0fd9b8a7b130b0b45cb5fdf7e2f29cf | dfd0d55f42f50a10cda6fd9baa83690e88c2511a |
| `character_sets_dir` | /usr/share/mysql-8.0/charsets/ | /usr/share/mysql-8.4/charsets/ |
| `general_log_file` | /var/lib/mysql/51a1645acb81.log | /var/lib/mysql/042757887f10.log |
| `group_replication_consistency` | EVENTUAL | BEFORE_ON_PRIMARY_FAILOVER |
| `innodb_adaptive_hash_index` | ON | OFF |
| `innodb_buffer_pool_in_core_file` | ON | OFF |
| `innodb_change_buffering` | all | none |
| `innodb_doublewrite_pages` | 4 | 128 |
| `innodb_flush_method` | fsync | O_DIRECT |
| `innodb_io_capacity` | 200 | 10000 |
| `innodb_io_capacity_max` | 2000 | 20000 |
| `innodb_log_buffer_size` | 16777216 | 67108864 |
| `innodb_read_io_threads` | 4 | 11 |
| `innodb_use_fdatasync` | OFF | ON |
| `innodb_version` | 8.0.42 | 8.4.7 |
| `lc_messages_dir` | /usr/share/mysql-8.0/ | /usr/share/mysql-8.4/ |
| `optimizer_switch` | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on,hash_set_operations=on |
| `performance_schema_error_size` | 5319 | 5550 |
| `performance_schema_max_memory_classes` | 450 | 470 |
| `performance_schema_max_rwlock_classes` | 60 | 100 |
| `performance_schema_max_statement_classes` | 219 | 220 |
| `pid_file` | /var/lib/mysql/51a1645acb81.pid | /var/lib/mysql/042757887f10.pid |
| `relay_log` | 51a1645acb81-relay-bin | 042757887f10-relay-bin |
| `relay_log_basename` | /var/lib/mysql/51a1645acb81-relay-bin | /var/lib/mysql/042757887f10-relay-bin |
| `relay_log_index` | /var/lib/mysql/51a1645acb81-relay-bin.index | /var/lib/mysql/042757887f10-relay-bin.index |
| `slow_query_log_file` | /var/lib/mysql/51a1645acb81-slow.log | /var/lib/mysql/042757887f10-slow.log |
| `temptable_max_mmap` | 1073741824 | 0 |
| `temptable_use_mmap` | ON | OFF |

### 4.3. MySQL 8.4.7에 추가된 변수

| 변수명 |
|---|
| `explain_json_format_version` |
| `performance_schema_max_meter_classes` |
| `performance_schema_max_metric_classes` |
| `restrict_fk_on_non_standard_key` |
| `set_operations_buffer_size` |
| `tls_certificates_enforced_validation` |

### 4.4. MySQL 8.0.42에서 제거된 변수

| 변수명 |
|---|
| `avoid_temporal_upgrade` |
| `binlog_transaction_dependency_tracking` |
| `default_authentication_plugin` |
| `expire_logs_days` |
| `have_openssl` |
| `have_ssl` |
| `log_bin_use_v1_row_events` |
| `master_info_repository` |
| `new` |
| `old` |
| `relay_log_info_file` |
| `relay_log_info_repository` |
| `show_old_temporals` |
| `slave_rows_search_algorithms` |
| `transaction_write_set_extraction` |

## 5. 인증 방식 변경 및 대응 (Authentication Fix & Impact)

MySQL 8.4에서는 `caching_sha2_password`가 기본 인증 플러그인으로 사용됩니다. 테스트 과정에서 발견된 이슈와 해결 과정을 기록합니다.

### 5.1. 이슈 현황
- **현상:** `sha2_user` 접속 시 `'cryptography' package is required for sha256_password or caching_sha2_password` 오류 발생하며 접속 실패.
- **원인:** Python 환경에 `caching_sha2_password` 처리를 위한 `cryptography` 패키지가 누락됨.

### 5.2. 해결 과정 및 결과
1. **패키지 설치:** Python 환경(`requirements.txt`)에 `cryptography` 패키지 추가 및 설치.
2. **재시험 결과:** `sha2_user`가 MySQL 8.0 및 8.4 모두에서 **정상 접속 성공** 확인.

### 5.3. 사용자 관점의 영향도 검토
> [!IMPORTANT]
> **MySQL 8.4 업그레이드 시 주의 사항**
> 1. **클라이언트 라이브러리 의존성:** Python 등 클라이언트 환경에서 `caching_sha2_password`를 지원하기 위한 추가 라이브러리(예: `cryptography`)가 필요할 수 있습니다.
> 2. **Native Password 지원 중단:** MySQL 8.4에서는 `mysql_native_password` 플러그인이 기본적으로 비활성화되어 있습니다. 기존 `native_user` 방식의 계정은 접속이 실패하므로, `caching_sha2_password`로의 전환이 권장됩니다.