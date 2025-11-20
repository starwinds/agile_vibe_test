# 스프린트 계획 (Sprint 2)

## 1. 스프린트 정보

- **스프린트 기간:** 2025년 11월 20일 ~ 2025년 11월 27일 (1주)
- **스프린트 목표:** 고급 호환성 테스트 시나리오(메모리, 대용량 Payload)를 추가하고, Sprint 1에서 실패한 Pub/Sub 테스트를 안정화하여 테스트 커버리지를 높인다.
- **담당 팀/인원:** Gemini CLI (1명)

## 2. 스프린트 목표 (Sprint Goal)

> 이번 스프린트에서는 메모리 관리(Eviction)와 대용량 데이터 처리 시나리오를 추가하여 Redis와 Valkey 간의 미세한 동작 및 성능 차이를 측정할 수 있는 기능을 구현한다. 또한, 불안정했던 Pub/Sub 테스트를 수정하여 전체 테스트 스위트의 신뢰도를 높인다.

## 3. Capacity 계획

- **총 개발 시간:** 5일 (주말 제외)
- **집중률:** 100%
- **총 Capacity:** 1.0 Person-Days/Day * 5 days = 5 PD

## 4. 스프린트 백로그 (Sprint Backlog)

| Epic | 사용자 스토리 | Task | 담당자 | 예상 시간 (PD) |
|---|---|---|---|---|
| **고급 호환성** | 4.1: Eviction 정책 비교 | Task 4.1.1: `memory_eviction.py` 생성 | Gemini | 1.5 |
| | | Task 4.1.2: `maxmemory` 설정/복원 로직 구현 | Gemini | (통합) |
| | | Task 4.1.3: 메트릭 수집 로직 구현 | Gemini | (통합) |
| | 4.2: 대용량 Payload 비교 | Task 4.2.1: `large_payloads.py` 생성 | Gemini | 1.5 |
| | | Task 4.2.2: 다양한 크기 Payload 생성 로직 구현 | Gemini | (통합) |
| | | Task 4.2.3: Latency 및 메모리 측정 로직 구현 | Gemini | (통합) |
| **안정화** | 4.3: Pub/Sub 테스트 수정 | Task 4.3.1: `pubsub.py` 디버깅 및 수정 | Gemini | 1.0 |
| **문서화** | 4.4: 문서 업데이트 | Task 4.4.2: `README.md`에 신규 시나리오 설명 추가 | Gemini | 0.5 |
| **총합** | | | | **4.5 PD** |

## 5. 완료의 정의 (Definition of Done - DoD)

- `memory_eviction.py`와 `large_payloads.py` 시나리오가 `app/scenarios`에 추가되어야 한다.
- 수정된 `pubsub.py` 테스트가 양쪽 타겟에서 모두 'OK' 상태로 통과해야 한다.
- `test_runner.py`를 실행하면 신규 시나리오 2종과 수정된 `pubsub` 테스트를 포함한 모든 테스트가 자동으로 실행되어야 한다.
- 테스트 결과로 `metrics`가 정상적으로 수집되고, 테이블 및 JSON 파일에 포함되어야 한다.
- `README.md`에 새로운 테스트 시나리오에 대한 설명이 추가되어야 한다.
- 모든 변경사항은 현재 브랜치에 커밋되어야 한다.
