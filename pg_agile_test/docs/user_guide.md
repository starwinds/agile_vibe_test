### 애플리케이션 실행 및 검증 가이드

이 가이드는 Docker 컨테이너를 통해 데이터베이스를 실행하고, Flask API 서버를 구동한 뒤, `curl` 명령어를 사용하여 API를 테스트하는 방법을 안내합니다.

**사전 준비:**
- `docker`가 설치 및 실행 중이어야 합니다.
- Python 가상환경이 `requirements.txt`를 기반으로 설정되어 있어야 합니다.

---

#### 1단계: 데이터베이스 실행

먼저, 터미널을 열고 아래 명령어를 실행하여 PostgreSQL + pgvector 데이터베이스를 Docker 컨테이너로 시작합니다.

```bash
# 기존에 실행 중인 컨테이너가 있다면 중지하고 삭제합니다.
docker rm -f pgvector-db

# 새 컨테이너를 백그라운드에서 실행합니다.
docker run -d --name pgvector-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 ankane/pgvector:latest
```
> **참고:** 데이터베이스가 완전히 시작되기까지 몇 초 정도 소요될 수 있습니다.

---

#### 2단계: API 서버 실행

새로운 터미널을 열고, 프로젝트의 루트 디렉토리에서 다음 명령어를 순서대로 실행하여 Flask API 서버를 시작합니다.

```bash
# 1. Python 가상환경을 활성화합니다.
source .venv/bin/activate

# 2. Flask 애플리케이션을 실행합니다.
#    PYTHONPATH를 현재 디렉토리로 설정하여 'src' 모듈을 찾을 수 있도록 합니다.
PYTHONPATH=. flask --app src/app run
```

서버가 성공적으로 실행되면 다음과 같은 메시지가 나타납니다:
```
 * Running on http://127.0.0.1:5000
```

---

#### 3단계: API 기능 테스트

이제 **별도의 새 터미널**을 열고 `curl` 명령어를 사용하여 실행 중인 API의 기능을 테스트합니다.

**3.1. 아이템 추가 (`POST /item`)**

아래 명령어를 실행하여 데이터베이스에 새로운 아이템 3개를 추가합니다.

```bash
# 아이템 1: AI 관련 책
curl -X POST http://127.0.0.1:5000/item \
-H "Content-Type: application/json" \
-d '{
    "item_name": "The AI Age",
    "category": "Technology",
    "content": "A deep dive into the world of artificial intelligence and machine learning."
}'

# 아이템 2: 요리책
curl -X POST http://127.0.0.1:5000/item \
-H "Content-Type: application/json" \
-d '{
    "item_name": "Simple Recipes",
    "category": "Cooking",
    "content": "Easy and delicious meals for everyday cooking."
}'

# 아이템 3: 기술 관련 다른 책
curl -X POST http://127.0.0.1:5000/item \
-H "Content-Type: application/json" \
-d '{
    "item_name": "Python for Pros",
    "category": "Technology",
    "content": "Advanced programming techniques in Python."
}'
```
각각의 요청에 대해 `{"message":"Item added successfully"}` 메시지를 받으면 성공입니다.

**3.2. 아이템 검색 (`GET /search`)**

이제 저장된 데이터를 대상으로 유사도 검색 및 필터링을 테스트합니다.

**A) '인공지능'과 유사한 아이템 검색**
```bash
curl -G http://127.0.0.1:5000/search --data-urlencode "query=artificial intelligence"
```
> 예상 결과: "The AI Age"가 가장 높은 유사도 점수와 함께 반환됩니다.

**B) '프로그래밍'과 유사하면서 'Technology' 카테고리에 속하는 아이템 검색**
```bash
curl -G http://127.0.0.1:5000/search --data-urlencode "query=programming" --data-urlencode "category=Technology"
```
> 예상 결과: "Python for Pros"와 "The AI Age"가 유사도 순으로 반환됩니다.

**C) '요리'와 관련된 아이템 검색**
```bash
curl -G http://127.0.0.1:5000/search --data-urlencode "query=cooking"
```
> 예상 결과: "Simple Recipes"가 반환됩니다.

---

#### 4단계 (선택): 자동화된 테스트 실행

구현된 모든 기능은 `pytest`로 자동화된 테스트가 작성되어 있습니다. 아래 명령어로 모든 테스트를 실행해볼 수 있습니다.

```bash
# (API 서버가 실행 중인 터미널은 그대로 두고) 새 터미널에서 실행합니다.
# 가상환경 활성화
source .venv/bin/activate

# pytest 실행
pytest -v
```

---

#### 5단계: 서비스 종료

테스트가 끝나면 아래 방법으로 서비스를 종료할 수 있습니다.

1.  **API 서버 종료:** `flask`가 실행 중인 터미널에서 `Ctrl + C`를 누릅니다.
2.  **데이터베이스 컨테이너 중지:** 아래 명령어를 실행합니다.
    ```bash
    docker stop pgvector-db
    ```
