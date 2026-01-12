# MySQL 8.0 vs 8.4 통합 비교 리포트 (Standalone & Cluster)
> **보고서 생성일:** 2026-01-12 15:05:29

## 1. 개요
본 리포트는 Standalone 환경과 InnoDB Cluster 환경에서의 MySQL 8.0.42와 8.4.7 버전 간 차이점을 통합 분석한 결과입니다.

> **참고:** 파일 경로, 호스트명, UUID, 빌드 정보 등 환경 종속적이거나 매 실행마다 달라지는 변수는 제외되었습니다.

## 2. Version-driven Diff (기본 버전 차이)
Standalone 환경과 Cluster 환경에서 공통적으로 관찰되거나, MySQL 버전 업그레이드 자체에 기인한 변경 사항입니다.

 총 **17** 개의 파라미터가 변경되었습니다.

| 변수명 | MySQL 8.0 | MySQL 8.4 | 비고 |
|---|---|---|---|
| `group_replication_consistency` | EVENTUAL | BEFORE_ON_PRIMARY_FAILOVER |  |
| `innodb_change_buffering` | all | none |  |
| `innodb_doublewrite_pages` | 4 | 128 |  |
| `innodb_flush_method` | fsync | O_DIRECT |  |
| `innodb_io_capacity` | 200 | 10000 |  |
| `innodb_io_capacity_max` | 2000 | 20000 |  |
| `innodb_log_buffer_size` | 16777216 | 67108864 |  |
| `innodb_read_io_threads` | 4 | 11 |  |
| `innodb_use_fdatasync` | OFF | ON |  |
| `innodb_version` | 8.0.42 | 8.4.7 |  |
| `optimizer_switch` | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on | index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,engine_condition_pushdown=on,index_condition_pushdown=on,mrr=on,mrr_cost_based=on,block_nested_loop=on,batched_key_access=off,materialization=on,semijoin=on,loosescan=on,firstmatch=on,duplicateweedout=on,subquery_materialization_cost_based=on,use_index_extensions=on,condition_fanout_filter=on,derived_merge=on,use_invisible_indexes=off,skip_scan=on,hash_join=on,subquery_to_derived=off,prefer_ordering_index=on,hypergraph_optimizer=off,derived_condition_pushdown=on,hash_set_operations=on |  |
| `performance_schema_error_size` | 5319 | 5550 |  |
| `performance_schema_max_memory_classes` | 450 | 470 |  |
| `performance_schema_max_rwlock_classes` | 60 | 100 |  |
| `performance_schema_max_statement_classes` | 219 | 220 |  |
| `temptable_max_mmap` | 1073741824 | 0 |  |
| `temptable_use_mmap` | ON | OFF |  |

## 3. Cluster-driven Diff (클러스터 환경 특화)
InnoDB Cluster 구성으로 인해 추가적으로 발생하거나 변경된 파라미터입니다. (Primary Node 기준)

 총 **5** 개의 파라미터가 변경되었습니다.

| 변수명 | MySQL 8.0 (Cluster) | MySQL 8.4 (Cluster) | 비고 |
|---|---|---|---|
| `group_replication_exit_state_action` | READ_ONLY | OFFLINE_MODE |  |
| `host_cache_size` | 279 | 0 |  |
| `relay_log` | mysql80-1-relay-bin | mysql84-1-relay-bin | Standalone: bb23c69d6eff-relay-bin -> 55643a4a662c-relay-bin |
| `server_id` | 1 | 11 |  |
| `version` | 8.0.42 | 8.4.7 |  |