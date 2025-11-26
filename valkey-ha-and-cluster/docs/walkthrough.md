# Valkey HA 및 Cluster 동작 검증 결과

## 개요
Valkey HA(Sentinel) 및 Cluster 환경의 동작을 검증했습니다. Docker Compose를 사용하여 환경을 구축하고, Python 테스트 클라이언트를 컨테이너로 실행하여 기능을 확인했습니다.

## 환경 설정 변경 사항

### HA 환경
- **Sentinel 설정:** `sentinel-entrypoint.sh`를 수정하여 마스터 IP를 동적으로 resolve하도록 변경
- **Docker Compose:** `replica-announce-ip` 및 `replica-announce-port` 설정 추가
- **테스트 클라이언트:** Docker 컨테이너로 실행하여 내부 네트워크 접근 문제 해결

### Cluster 환경
- **테스트 클라이언트:** `cluster_test.py`를 Docker 컨테이너로 실행하도록 설정

## 테스트 결과

### 1. HA (Sentinel) 테스트

#### 성공한 기능
- ✅ **Sentinel 연결:** Sentinel을 통해 마스터 및 레플리카 발견 성공
- ✅ **CRUD 작업:** 마스터에 데이터 쓰기 및 읽기 성공
- ✅ **복제 확인:** 레플리카에서 데이터 읽기 성공, 마스터와 동기화 확인

#### 제한 사항
- ⚠️ **Failover 테스트:** 컨테이너 내부에서 `docker kill` 명령을 실행할 수 없어 자동 Failover 검증 불가
  - 수동으로 호스트에서 `docker kill valkey-master` 실행 시 Sentinel이 새 마스터를 선출하는 것은 확인됨

### 2. Cluster 테스트

#### 성공한 기능
- ✅ **클러스터 연결:** 6개 노드(Primary 3, Replica 3) 클러스터 구성 성공
- ✅ **키 분산:** 20개의 키를 클러스터 전체에 분산 저장 성공
- ✅ **리디렉션:** `MOVED` 리디렉션이 자동으로 처리되어 키 조회/저장 성공

#### 제한 사항
- ⚠️ **키 분산 통계:** `redis-py-cluster` 라이브러리의 `get_nodes()` 메서드 미지원으로 노드별 키 분포 확인 불가
- ⚠️ **Failover 테스트:** `keyslot()` 메서드 미지원 및 Docker 명령 제약으로 자동 Failover 검증 불가

## 결론
Valkey HA 및 Cluster의 핵심 기능(데이터 저장/조회, 복제, 분산)이 정상적으로 작동함을 확인했습니다. 자동 Failover 기능은 환경 제약으로 인해 완전히 검증하지 못했으나, 인프라 구성은 정상적으로 완료되었습니다.

## 향후 개선 사항
1. `redis` 라이브러리를 최신 버전으로 업그레이드하여 API 호환성 개선
2. Failover 테스트를 위한 별도의 관리 컨테이너 추가 고려
3. 호스트 네트워크 모드 사용 또는 포트 매핑 최적화 검토
