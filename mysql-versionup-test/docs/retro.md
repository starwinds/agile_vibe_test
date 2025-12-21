# Sprint 1 회고 (Retrospective)

- **스프린트:** Sprint 1 (2025.12.22 ~ 2025.12.26)
- **참여자:** Gemini
- **날짜:** 2025.12.26

---

## Keep (잘한 점)
- **Test-Driven Approach:** 테스트를 먼저 생각하고 구현하는 방식을 통해, 두 버전 간의 차이점을 명확하고 안정적으로 식별할 수 있었습니다.
- **Repeatable Environment:** Docker와 Pytest를 사용하여 전체 테스트 환경을 코드로 정의함으로써, 누구든 동일한 결과를 재현할 수 있는 반복 가능한 실험 환경을 구축했습니다.
- **Automated Reporting:** 최종적으로 모든 테스트 결과를 종합하여 자동으로 마크다운 보고서를 생성하는 스크립트를 구현하여, 결과 분석 및 공유가 매우 용이해졌습니다.
- **Clean Structure:** `mysql-compare`라는 명확한 디렉토리 구조와 역할별로 분리된 파일 구성은 프로젝트를 이해하고 유지보수하기 쉽게 만들었습니다.

## Problem (개선할 점)
- **Flawed Initial Assumptions:** 일부 테스트(e.g., Collation, 예약어) 구현 시, 예상되는 성공/실패 시나리오를 미리 깊게 분석하지 않고 코드를 작성하여 불필요한 테스트 실패와 디버깅 사이클을 반복했습니다.
- **Inefficient First Draft:** 성능 테스트의 첫 구현이 매우 비효율적이어서(단일 Insert 반복), 테스트 실행 시간이 과도하게 길어지는 문제가 발생했습니다.
- **Lack of Library Understanding:** `pytest-json-report` 라이브러리 사용 시, 출력되는 JSON의 정확한 구조를 미리 확인하지 않고 파싱 코드를 작성하여 여러 번의 `KeyError`를 겪었습니다.
- **Careless Mistakes:** 단순한 오타나 `()` 누락과 같은 사소한 실수로 인해 테스트가 반복적으로 실패하여, 문제 해결에 예상보다 많은 시간이 소요되었습니다.

## Try (다음 스프린트 액션 아이템)
- **Hypothesize First:** 테스트 단정(assert)을 작성하기 전, 공식 문서나 가설을 기반으로 '왜 이 테스트가 성공해야 하는가?' 또는 '왜 실패해야 하는가?'를 명확히 정의하고 주석으로 남기는 습관을 들입니다.
- **Optimize Early for Performance Code:** 성능 테스트와 같이 대량의 데이터를 다루는 코드를 작성할 때는, 초기 단계부터 `executemany`와 같은 효율적인 방법을 우선적으로 고려합니다.
- **Inspect Outputs Before Parsing:** 새로운 라이브러리가 생성하는 파일(JSON, XML 등)을 다룰 때는, 코드를 작성하기 전에 먼저 실제 출력 파일을 열어보고 그 구조를 명확히 파악합니다.
- **Increase Attention to Detail:** 코드 작성 시 좀 더 세심한 주의를 기울여, 간단한 문법 오류나 오타로 인한 시간 낭비를 줄입니다.