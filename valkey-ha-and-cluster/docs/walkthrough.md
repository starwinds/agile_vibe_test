# Valkey HA 및 Cluster 동작 검증 결과

## 개요
Valkey HA(Sentinel) 및 Cluster 환경의 동작을 검증했습니다. Docker Compose를 사용하여 환경을 구축하고, Python 테스트 클라이언트를 컨테이너로 실행하여 기능을 확인했습니다.

## 환경 설정 변경 사항

### HA 환경
- **Sentinel 설정:** `sentinel-entrypoint.sh`를 수정하여 마스터 IP를 동적으로 resolve하도록 변경
- **Docker Compose:** Docker 소켓(`/var/run/docker.sock`)을 테스트 컨테이너에 마운트
- **Dockerfile:** Docker CLI 설치 추가
- **테스트 클라이언트:** Docker 컨테이너로 실행하여 내부 네트워크 접근 문제 해결

### Cluster 환경
- **Docker Compose:** Docker 소켓 마운트 추가
- **Dockerfile:** Docker CLI 설치 추가
- **테스트 클라이언트:** `cluster_test.py`를 Docker 컨테이너로 실행하도록 설정

## 테스트 결과

### 1. HA (Sentinel) 테스트

#### 성공한 기능
- ✅ **Sentinel 연결:** Sentinel을 통해 마스터 및 레플리카 발견 성공
- ✅ **CRUD 작업:** 마스터에 데이터 쓰기 및 읽기 성공
- ✅ **복제 확인:** 레플리카에서 데이터 읽기 성공, 마스터와 동기화 확인
- ✅ **자동 Failover:** 마스터 종료 시 Sentinel이 레플리카를 새 마스터로 승격
  - 이전 마스터: `172.23.0.2:6379`
  - 새 마스터: `172.23.0.6:6379`
  - Sentinel 로그에서 `+promoted-slave` 및 `+failover-end` 확인

### 2. Cluster 테스트

#### 성공한 기능
- ✅ **클러스터 연결:** 6개 노드(Primary 3, Replica 3) 클러스터 구성 성공
- ✅ **키 분산:** 20개의 키를 클러스터 전체에 분산 저장 성공
- ✅ **리디렉션:** `MOVED` 리디렉션이 자동으로 처리되어 키 조회/저장 성공

#### 제한 사항
- ⚠️ **키 분산 통계:** `redis-py-cluster` 라이브러리의 `get_nodes()` 메서드 미지원으로 노드별 키 분포 확인 불가
- ⚠️ **Failover 테스트:** `keyslot()` 메서드 미지원으로 자동 Failover 검증 불가

## 결론
Valkey HA의 핵심 기능(데이터 저장/조회, 복제, **자동 Failover**)이 정상적으로 작동함을 확인했습니다. Cluster의 기본 기능(분산, 리디렉션)도 검증되었으나, Failover는 라이브러리 제약으로 완전히 검증하지 못했습니다.

## 향후 개선 사항
1. `redis-py-cluster` 대신 최신 `redis-py` 라이브러리로 업그레이드하여 Cluster 기능 완전 지원
2. 프로덕션 환경에서는 Docker 소켓 마운트 대신 다른 방식의 Failover 테스트 고려
