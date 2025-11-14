# pgvector-python-app

이 프로젝트는 PostgreSQL + pgvector를 사용하여 문장 임베딩을 저장하고 검색하는 Python 애플리케이션입니다.

## ⚙️ 설정 방법

### 1. PostgreSQL (Docker)
아래 명령어를 실행하여 `pgvector`가 포함된 PostgreSQL Docker 컨테이너를 시작합니다.

```bash
docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ankane/pgvector:latest
```

### 2. Python 가상환경 및 의존성 설치
Python 3 가상환경을 설정하고 `requirements.txt`에 명시된 패키지를 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🧪 테스트 실행

프로젝트의 모든 테스트를 실행하고 코드 커버리지를 확인하려면 아래 명령어를 사용하세요.

```bash
pytest --cov=src -v
```

## 🚀 실행

(추후 Flask 애플리케이션 실행 방법 추가 예정)

```