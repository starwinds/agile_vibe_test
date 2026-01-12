# MySQL 8.0 vs 8.4 통합 비교 리포트 (Standalone & Cluster)
> **보고서 생성일:** 2026-01-12 14:23:22

## 1. 개요
본 리포트는 Standalone 환경과 InnoDB Cluster 환경에서의 MySQL 8.0.42와 8.4.7 버전 간 차이점을 통합 분석한 결과입니다.

## 2. Version-driven Diff (기본 버전 차이)
Standalone 환경과 Cluster 환경에서 공통적으로 관찰되거나, MySQL 버전 업그레이드 자체에 기인한 변경 사항입니다.

 총 **23** 개의 파라미터가 변경되었습니다.

| 변수명 | MySQL 8.0 | MySQL 8.4 | 비고 |
|---|---|---|---|
| `build_id` | cd3aff82d0fd9b8a7b130b0b45cb5fdf7e2f29cf | dfd0d55f42f50a10cda6fd9baa83690e88c2511a |  |
| `character_sets_dir` | /usr/share/mysql-8.0/charsets/ | /usr/share/mysql-8.4/charsets/ |  |
| `group_replication_consistency` | EVENTUAL | BEFORE_ON_PRIMARY_FAILOVER |  |
| `innodb_adaptive_hash_index` | ON | OFF |  |
| `innodb_buffer_pool_in_core_file` | ON | OFF |  |
| `innodb_change_buffering` | all | none |  |
| `innodb_doublewrite_pages` | 4 | 128 |  |
| `innodb_flush_method` | fsync | O_DIRECT |  |
| `innodb_io_capacity` | 200 | 10000 |  |
| `innodb_io_capacity_max` | 2000 | 20000 |  |
| `innodb_log_buffer_size` | 16777216 | 67108864 |  |
| `innodb_read_io_threads` | 4 | 11 |  |
| `innodb_use_fdatasync` | OFF | ON |  |
| `innodb_version` | 8.0.42 | 8.4.7 |  |
| `lc_messages_dir` | /usr/share/mysql-8.0/ | /usr/share/mysql-8.4/ |  |
| `optimizer_switch` | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on,hash_set_operations=on |  |
| `performance_schema_error_size` | 5319 | 5550 |  |
| `performance_schema_max_memory_classes` | 450 | 470 |  |
| `performance_schema_max_rwlock_classes` | 60 | 100 |  |
| `performance_schema_max_statement_classes` | 219 | 220 |  |
| `pid_file` | /var/lib/mysql/bb23c69d6eff.pid | /var/lib/mysql/55643a4a662c.pid | Standalone Only |
| `temptable_max_mmap` | 1073741824 | 0 |  |
| `temptable_use_mmap` | ON | OFF |  |

## 3. Cluster-driven Diff (클러스터 환경 특화)
InnoDB Cluster 구성으로 인해 추가적으로 발생하거나 변경된 파라미터입니다. (Primary Node 기준)

 총 **16** 개의 파라미터가 변경되었습니다.

| 변수명 | MySQL 8.0 (Cluster) | MySQL 8.4 (Cluster) | 비고 |
|---|---|---|---|
| `general_log_file` | /var/lib/mysql/mysql80-1.log | /var/lib/mysql/mysql84-1.log | Standalone: /var/lib/mysql/bb23c69d6eff.log -> /var/lib/mysql/55643a4a662c.log |
| `group_replication_exit_state_action` | READ_ONLY | OFFLINE_MODE |  |
| `group_replication_group_name` | 6338999b-ef76-11f0-b7cf-b25fd60fabfe | 7a5c6cbc-ef76-11f0-8bc9-befeb659b4f2 |  |
| `group_replication_group_seeds` | mysql80-3:3306,mysql80-2:3306 | mysql84-3:3306,mysql84-2:3306 |  |
| `group_replication_local_address` | mysql80-1:3306 | mysql84-1:3306 |  |
| `group_replication_view_change_uuid` | 63389d8a-ef76-11f0-b7cf-b25fd60fabfe | AUTOMATIC |  |
| `gtid_executed` | 4c6f38a6-ef76-11f0-85f6-b25fd60fabfe:1-9,
6338999b-ef76-11f0-b7cf-b25fd60fabfe:1-80,
63389d8a-ef76-11f0-b7cf-b25fd60fabfe:1-5 | 4c7020bd-ef76-11f0-893e-befeb659b4f2:1-9,
7a5c6cbc-ef76-11f0-8bc9-befeb659b4f2:1-80 |  |
| `host_cache_size` | 279 | 0 |  |
| `hostname` | mysql80-1 | mysql84-1 |  |
| `relay_log` | mysql80-1-relay-bin | mysql84-1-relay-bin | Standalone: bb23c69d6eff-relay-bin -> 55643a4a662c-relay-bin |
| `relay_log_basename` | /var/lib/mysql/mysql80-1-relay-bin | /var/lib/mysql/mysql84-1-relay-bin | Standalone: /var/lib/mysql/bb23c69d6eff-relay-bin -> /var/lib/mysql/55643a4a662c-relay-bin |
| `relay_log_index` | /var/lib/mysql/mysql80-1-relay-bin.index | /var/lib/mysql/mysql84-1-relay-bin.index | Standalone: /var/lib/mysql/bb23c69d6eff-relay-bin.index -> /var/lib/mysql/55643a4a662c-relay-bin.index |
| `server_id` | 1 | 11 |  |
| `server_uuid` | 4c6f38a6-ef76-11f0-85f6-b25fd60fabfe | 4c7020bd-ef76-11f0-893e-befeb659b4f2 |  |
| `slow_query_log_file` | /var/lib/mysql/mysql80-1-slow.log | /var/lib/mysql/mysql84-1-slow.log | Standalone: /var/lib/mysql/bb23c69d6eff-slow.log -> /var/lib/mysql/55643a4a662c-slow.log |
| `version` | 8.0.42 | 8.4.7 |  |