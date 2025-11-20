# PRD2 – Redis 7.2.6 ↔ Valkey 9.0  
## Sprint #2: 확장 호환성 테스트 시나리오 구현 요구사항 (Gemini CLI 전달용)

본 문서는 Sprint #2에서 Gemini CLI가 수행해야 할 **추가 테스트 시나리오 구현 요구사항(PRD)** 입니다.  
Redis 7.2.6과 Valkey 9.0의 디테일한 차이를 검출하기 위해 설계되었습니다.

---

# 📌 1. Sprint #2 개요

### 🎯 목적  
Redis 7.2.6과 Valkey 9.0 사이의 미세한 동작 차이를 감지할 수 있는 **고급 테스트 시나리오 2종**을 추가 구현한다.

### 🧩 역할 정의  
Gemini CLI는 다음 역할로 행동해야 한다:

- Python 기반 자동 테스트 엔지니어  
- Redis/Valkey 호환성 분석자  
- Sprint #1에서 구축된 테스트 프레임워크를 확장하는 개발자  

---

# 🧱 2. 기존 프로젝트 구조 (Sprint #1)

```
redis-valkey-compat/
 ├─ docker-compose.yml
 ├─ app/
 │   ├─ requirements.txt
 │   ├─ config.py
 │   ├─ test_runner.py
 │   └─ scenarios/
 │       ├─ basic_crud.py
 │       ├─ data_structures.py
 │       ├─ scan_and_iter.py
 │       ├─ pubsub.py
 │       ├─ lua_and_tx.py
 │       └─ __init__.py
```

Sprint #2에서는 여기에서 `scenarios` 아래 새 파일 2개를 추가한다.

---

# 🚀 3. Sprint #2에서 구현할 신규 시나리오

---

# 3.1 시나리오 1️⃣: 메모리 압박 + Eviction 정책 테스트  
📄 파일명: `app/scenarios/memory_eviction.py`

## ✔ 목적  
Redis vs Valkey에서 **maxmemory + eviction 정책(allkeys-lru)** 적용 시  
- eviction 발생 여부  
- eviction된 key 개수  
- 생존한 key의 패턴  
- 메모리 사용량 변화  

등에서 차이가 발생하는지 검증.

## ✔ 테스트 흐름  
1. 대략 1MB 크기의 payload를 가진 `bigkey:N` 키를 대량 생성  
2. `maxmemory`에 도달하도록 압박하여 eviction 유발  
3. eviction 이후:
   - SCAN 전체 key 개수 기록  
   - memory usage 샘플링  
4. metrics로 다음 값 반환:
   - keys_before / keys_after
   - evicted_count
   - memory_samples 목록
   - valkey vs redis 차이 포착

## ✔ 함수 규격  

```
def run(client) -> dict:
    {
        "scenario": "memory_eviction",
        "status": "OK" | "WARN" | "FAIL",
        "detail": "...",
        "metrics": {
            "keys_before": N,
            "keys_after": M,
            "evicted_count": X,
            "memory_samples": [...]
        }
    }
```

---

# 3.2 시나리오 2️⃣: 대용량 Payload 테스트  
📄 파일명: `app/scenarios/large_payloads.py`

## ✔ 목적  
Payload 크기에 따라 Redis vs Valkey가  
- 성능(latency)  
- memory usage  
- 내부 encoding  

에서 차이를 보이는지 확인한다.

## ✔ 테스트 흐름  
Payload size 목록: `[1KB, 32KB, 256KB, 1MB, 5MB]`

각 size에 대해:

1. payload 생성  
2. SET latency 측정  
3. GET latency 측정  
4. MEMORY USAGE 기록  
5. redis/valkey 결과 비교 가능한 metrics 구조로 저장  

## ✔ 함수 규격  

```
def run(client) -> dict:
    {
        "scenario": "large_payloads",
        "status": "OK" | "WARN" | "FAIL",
        "detail": "...",
        "metrics": {
            "1KB": {"set_ms": x, "get_ms": y, "memory_usage": z},
            "32KB": {...},
            "256KB": {...},
            "1MB": {...},
            "5MB": {...}
        }
    }
```

---

# 🔧 4. 공통 구현 요구사항

- 테스트 실패 여부와 무관하게 항상 dict 출력  
- 테스트마다 cleanup 수행 (SCAN → DEL)  
- 성능 측정은 `time.perf_counter()` 사용  
- 실행 시간 과도하지 않도록 구성 (각 size 3회 반복)  
- 충분한 주석 포함  
- metrics는 test_runner의 JSON 및 테이블 출력에 적합하게 구성  

---

# 🔗 5. test_runner.py 수정 요구사항  

Gemini는 두 신규 시나리오를 자동 실행하도록 `test_runner.py`를 수정해야 한다:

- 신규 import 추가  
- scenarios 리스트/맵에 포함  
- 테이블 출력 시 신규 시나리오가 표시되도록 보장  

형식 예:

```
--- 패치: test_runner.py ---
```python
# (import 및 scenario 등록 코드)
```

---

# 📝 6. Gemini CLI에서 반드시 따라야 하는 출력 형식

Gemini는 아래 형식으로 파일들을 생성해야 한다:

```
--- 파일: app/scenarios/memory_eviction.py ---
```python
# (전체 Python 코드)
```

--- 파일: app/scenarios/large_payloads.py ---
```python
# (전체 Python 코드)
```

--- 패치: test_runner.py ---
```python
# (수정 코드)
```

출력 누락 금지.

---

# 📅 7. Sprint #2 Definition of Done (DoD)

- memory_eviction.py 정상 생성  
- large_payloads.py 정상 생성  
- test_runner.py에서 자동 실행  
- Redis 7.2.6 vs Valkey 9.0 차이가 metrics로 관찰 가능  
- README에 Sprint #2 시나리오 설명 추가  
- 로컬 PC에서 테스트 반복 실행 가능  

---

# 📦 8. 사용 용도  

이 문서는 **Gemini CLI에게 바로 전달되는 PRD 문서**입니다.  
Gemini가 Sprint #2 개발 작업을 정확히 수행할 수 있도록 상세 명세를 제공합니다.
