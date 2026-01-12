# [Gemini CLI Task] MySQL InnoDB Cluster 비교 테스트 (Primary-only 기준)

## 1. 작업 목적 (Objective)

기존에 완료된 **Standalone MySQL 8.0.42 vs 8.4.7 비교 테스트**에 이어,
본 작업의 목적은 **DBaaS 제공 형태인 InnoDB Cluster(+ MySQL Router)** 환경에서

- MySQL 8.0.42 vs 8.4.7 간
- **GLOBAL VARIABLES의 기본값 및 동작 차이**

를 비교·분석하는 것이다.

⚠️ 본 단계에서는 **Primary 노드의 GLOBAL VARIABLES만을 기준으로 수집·비교**한다.
Secondary 노드는 역할(role) 및 상태(state)에 따라 값이 달라질 수 있으므로,
이번 단계의 비교 범위에서는 제외한다.

---

## 2. 설계 원칙 (Design Principles)

### 2.1 Primary-only 기준 수집 (중요)

- InnoDB Cluster에서 **Primary 노드는 설정/동작의 기준(source of truth)** 이다.
- DBaaS 운영 정책, 파라미터 템플릿, 고객 영향 분석은 **Primary 기준으로 정의**된다.
- 따라서 본 비교 테스트에서는:
  - ❌ Secondary GLOBAL VARIABLES는 기본 수집 대상이 아님
  - ✅ Primary GLOBAL VARIABLES만 수집·비교

Secondary 노드는 추후 단계(확장 단계)에서
- Failover 검증
- Role/State-driven noise 분석
를 목적으로 **선택적으로 추가**할 수 있다.

---

## 3. 비교 대상 및 범위

### 3.1 MySQL 버전
- MySQL 8.0.42 (InnoDB Cluster)
- MySQL 8.4.7 (InnoDB Cluster)

### 3.2 Cluster 구성
- InnoDB Cluster (Group Replication 기반)
- MySQL Router 포함
- 3-node cluster 권장 (Primary 1 + Secondary 2)

### 3.3 비교 범위
- `SHOW GLOBAL VARIABLES` 결과
- **Primary 노드 기준**
- Cluster/Group Replication 활성화로 인해 노출/변경되는 변수 포함

### 3.4 제외 범위 (이번 단계)
- Secondary 노드 GLOBAL VARIABLES
- system schema 구조 비교
- 성능 벤치마크(TPS/Latency)
- FK/DDL strictness 테스트

---

## 4. 환경 제약 (Execution Environment)

- OS: Windows + WSL2 (Ubuntu)
- MySQL 실행 방식: Docker Compose
- Cluster 구성: MySQL Shell 사용
- 비교 자동화: Python
- 상용 도구 사용 금지
- 로컬 환경에서 재현 가능해야 함

---

## 5. 사전 조건 (Preconditions)

1. InnoDB Cluster가 정상 구성되어 있어야 함
2. Cluster 상태 확인:
   ```sql
   SELECT
     MEMBER_ID, MEMBER_ROLE, MEMBER_STATE
   FROM performance_schema.replication_group_members;
   ```
   - 모든 멤버가 `ONLINE`
   - 정확히 1개의 `PRIMARY` 존재

3. 비교 대상 GLOBAL VARIABLES는 반드시
   - **PRIMARY 노드에서만** 수집할 것

---

## 6. 데이터 수집 요구사항

### 6.1 Primary 노드 식별

- MySQL Shell 또는 SQL을 통해 Primary 노드를 식별
- Primary 노드의 host/port 정보를 명확히 기록

### 6.2 GLOBAL VARIABLES 수집

Primary 노드에서 다음 SQL 실행:

```sql
SHOW GLOBAL VARIABLES;
```

### 6.3 결과 저장 형식

버전별로 JSON 파일 생성:

- `cluster_primary_global_variables_8_0_42.json`
- `cluster_primary_global_variables_8_4_7.json`

각 JSON 항목은 최소 다음 정보를 포함해야 함:

- variable_name
- value

---

## 7. 비교/분석 요구사항

### 7.1 Diff 기준

- Primary GLOBAL VARIABLES 기준
- 8.0.42 vs 8.4.7 값 비교

### 7.2 Diff 분류

비교 결과는 다음 두 가지로 분류:

1. **Version-driven Diff**
   - Standalone 비교에서도 나타났던 차이
   - MySQL 버전 자체 변경에 기인

2. **Cluster-driven Diff**
   - InnoDB Cluster / Group Replication 활성화로 인해
     Primary에서만 의미를 가지는 변수 차이
   - 예: `group_replication_*` 계열, consistency 관련 변수 등

⚠️ Role/State-driven Diff는 이번 단계에서 다루지 않음

---

## 8. 산출물 (Deliverables)

### 8.1 Raw Data
- Primary GLOBAL VARIABLES JSON (버전별)
- Cluster 상태 스냅샷 (replication_group_members 결과)

### 8.2 비교 리포트 (Markdown)

파일명 예시:
```
mysql_cluster_primary_global_variables_diff_8_0_42_vs_8_4_7.md
```

필수 포함 섹션:
1. 테스트 환경 요약
2. Cluster 구성 및 Primary 확인 결과
3. Primary GLOBAL VARIABLES Diff 요약 테이블
4. Version-driven Diff 상세
5. Cluster-driven Diff 상세
6. DBaaS 운영 관점 코멘트
   - 파라미터 템플릿 반영 필요 여부
   - 고객 영향 가능성

---

## 9. 구현 가이드 (Python)

- 기존 Standalone 비교 코드 재사용 권장
- 최소 다음 함수 포함:
  - `detect_primary_node()`
  - `dump_global_variables(host)`
  - `diff_variables(v1, v2)`
- 실행 예시:
  ```bash
  python run_cluster_primary_compare.py --v1 8.0.42 --v2 8.4.7
  ```

---

## 10. 완료 기준 (Definition of Done)

- [ ] InnoDB Cluster가 자동으로 구성됨
- [ ] Primary 노드가 정확히 식별됨
- [ ] Primary GLOBAL VARIABLES만 수집됨
- [ ] 8.0.42 vs 8.4.7 diff가 재현 가능하게 생성됨
- [ ] Diff가 Version-driven / Cluster-driven으로 명확히 구분됨
- [ ] 결과가 DBaaS 기술 검토 자료로 바로 사용 가능함
