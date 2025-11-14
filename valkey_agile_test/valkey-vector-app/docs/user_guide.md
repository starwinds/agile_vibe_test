# Valkey 벡터 검색을 이용한 QA 서비스 사용자 가이드

이 문서는 Valkey 벡터 검색 기능을 활용한 QA 웹 애플리케이션을 설정하고 사용하는 방법을 안내합니다.

## 1. 소개

이 애플리케이션은 사용자가 질문을 입력하고, 사전에 추가된 문서들 중에서 가장 유사한 답변을 찾아 제공하는 간단한 QA(질의응답) 서비스입니다. 또한, 새로운 문서를 시스템에 추가하여 검색 가능한 지식 기반을 확장할 수 있습니다.

## 2. 전제 조건

시작하기 전에 다음 소프트웨어가 시스템에 설치되어 있는지 확인하십시오:

*   **Python 3.8+**
*   **pip** (Python 패키지 관리자)
*   **Docker**: Valkey 서버를 컨테이너로 실행하기 위해 필요합니다.

## 3. 설정

1.  **프로젝트 디렉토리로 이동:**
    ```bash
    cd /home/ubuntu/dev-proj/agile_vibe_test/valkey_agile_test/valkey-vector-app
    ```

2.  **Python 가상 환경 생성 및 활성화 (권장):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **필요한 라이브러리 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Valkey (VectorSearch 포함) 서버 실행 (Docker):**
    Docker가 설치되어 있고 실행 중인지 확인하십시오. 다음 명령을 사용하여 Valkey 서버를 백그라운드에서 실행합니다:
    ```bash
    docker run -d \
      --name valkey-vector \
      -p 6379:6379 \
      valkey/valkey:latest \
      --loadmodule /usr/lib/valkey/modules/vectorsearch.so
    ```
    *   `docker ps` 명령으로 `valkey-vector` 컨테이너가 실행 중인지 확인할 수 있습니다.
    *   이미 `valkey-vector`라는 이름의 컨테이너가 존재한다면, `docker rm -f valkey-vector`로 기존 컨테이너를 제거한 후 다시 실행하십시오.


## 4. 애플리케이션 실행

모든 설정이 완료되면, 다음 명령을 사용하여 Flask 애플리케이션을 실행할 수 있습니다:

```bash
source .venv/bin/activate && python3 -m src.app
```

애플리케이션 시작 시 Valkey 인덱스가 자동으로 생성됩니다.

애플리케이션이 성공적으로 시작되면, 터미널에 다음과 유사한 메시지가 표시됩니다:
```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## 5. 웹 인터페이스 사용

웹 브라우저를 열고 `http://127.0.0.1:5000/`으로 이동하십시오. 다음과 같은 인터페이스를 볼 수 있습니다:

### 5.1. 문서 추가 (Add a Document)

QA 서비스를 사용하기 전에 몇 가지 문서를 추가해야 합니다.

1.  **"Add a Document" 섹션:**
    *   `Document Content:` 텍스트 영역에 검색하고자 하는 문장이나 단락을 입력합니다.
    *   예시: `The capital of France is Paris.`
    *   `Add Document` 버튼을 클릭합니다.
2.  **결과 확인:**
    *   문서가 성공적으로 추가되면 `Success: Document added successfully (ID: [문서 ID])`와 같은 메시지가 표시됩니다.

### 5.2. 질문하기 (Ask a Question)

문서가 추가되면 질문을 할 수 있습니다.

1.  **"Ask a Question" 섹션:**
    *   `Question:` 입력 필드에 질문을 입력합니다.
    *   예시: `What is the capital of France?`
    *   `Ask` 버튼을 클릭합니다.
2.  **결과 확인:**
    *   시스템이 가장 유사한 문서를 찾아 `Answer:` 섹션에 해당 문서의 내용을 표시합니다.
    *   만약 유사한 문서를 찾지 못하면 `No similar documents found.` 메시지가 표시됩니다.

## 6. 문제 해결

*   **`Connection refused` 에러:** Valkey (또는 Redis) 서버가 실행 중인지 확인하십시오.
*   **`ModuleNotFoundError`:** `pip install -r requirements.txt` 명령을 실행하여 모든 종속성이 설치되었는지 확인하십시오. 가상 환경을 활성화했는지도 확인하십시오.
*   **`No similar documents found.`:** 질문과 관련된 문서가 충분히 추가되지 않았을 수 있습니다. "Add a Document" 기능을 사용하여 더 많은 문서를 추가해 보십시오.

이 가이드가 애플리케이션을 성공적으로 사용하는 데 도움이 되기를 바랍니다.