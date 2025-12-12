# Valkey Vector Search 테스트

Valkey의 공식 벡터 검색 모듈인 **Valkey-Search**를 테스트하기 위한 프로젝트입니다.

## 개요

이 프로젝트는 Valkey-Search 모듈의 다음 기능을 테스트합니다:
- 벡터 인덱스 생성
- 벡터 데이터 삽입
- KNN(K-Nearest Neighbors) 검색
- 하이브리드 쿼리 (벡터 검색 + 필터링)

## 사전 요구사항

- Docker 및 Docker Compose
- Python 3.8 이상
- `valkey-py` 라이브러리

## 설치

### 1. Python 가상환경 생성 및 의존성 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install valkey numpy
```

### 2. Docker 이미지 사용

두 가지 옵션이 있습니다:

#### 옵션 1: valkey-bundle (권장)
```bash
docker pull valkey/valkey-bundle
docker run --name valkey-search -p 6379:6379 -d valkey/valkey-bundle
```

#### 옵션 2: valkey-extensions
```bash
docker pull valkey/valkey-extensions
docker run --name valkey-search -p 6379:6379 -d valkey/valkey-extensions
```

#### 옵션 3: Docker Compose 사용
```bash
docker-compose up -d
```

## 사용법

### Valkey 서버 시작

```bash
# Docker Compose 사용
docker-compose up -d

# 서버 상태 확인
docker-compose ps
```

### 테스트 스크립트 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 실행
python test_valkey_vector_search.py
```

## 테스트 내용

### 1. 연결 테스트
Valkey 서버에 정상적으로 연결되는지 확인합니다.

### 2. 모듈 확인
Valkey-Search 모듈이 로드되어 있는지 확인합니다.

### 3. 벡터 인덱스 생성
128차원 벡터를 위한 HNSW 인덱스를 생성합니다.

```python
FT.CREATE vector_test_idx 
  ON HASH 
  PREFIX 1 vec: 
  SCHEMA embedding VECTOR HNSW 6 
    TYPE FLOAT32 
    DIM 128 
    DISTANCE_METRIC COSINE
```

### 4. 벡터 데이터 삽입
100개의 랜덤 벡터를 생성하여 삽입합니다.

### 5. 벡터 유사도 검색
쿼리 벡터와 가장 유사한 K개의 벡터를 검색합니다.

```python
FT.SEARCH vector_test_idx 
  "*=>[KNN 10 @embedding $query_vec]" 
  PARAMS 2 query_vec <vector_blob> 
  DIALECT 2
```

### 6. 하이브리드 검색
벡터 유사도 검색과 카테고리 필터링을 결합합니다.

```python
FT.SEARCH vector_test_idx 
  "@category:{cat_0}=>[KNN 10 @embedding $query_vec]" 
  PARAMS 2 query_vec <vector_blob> 
  DIALECT 2
```

## 주요 명령어

### Valkey-Search 명령어

```bash
# 인덱스 생성
FT.CREATE {index_name} ...

# 인덱스 삭제
FT.DROPINDEX {index_name}

# 인덱스 정보 조회
FT.INFO {index_name}

# 인덱스 목록 조회
FT._LIST

# 벡터 검색
FT.SEARCH {index_name} {query} ...
```

### Docker 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 로그 확인
docker-compose logs -f

# Valkey CLI 접속
docker exec -it valkey-search-test valkey-cli
```

## 성능 특징

- **지연 시간**: 단일 자릿수 밀리초
- **처리량**: 높은 QPS 지원
- **확장성**: 수십억 개의 벡터 처리 가능
- **정확도**: 99% 이상의 재현율

## 알고리즘

- **HNSW**: Approximate Nearest Neighbor 검색
- **KNN**: 정확한 K-Nearest Neighbors 검색

## 참고 자료

- [Valkey Search 공식 문서](https://valkey.io/topics/search/)
- [Valkey-Search GitHub](https://github.com/valkey-io/valkey-search)
- [Quick Start Guide](https://github.com/valkey-io/valkey-search/blob/main/QUICK_START.md)

## 라이선스

BSD-3-Clause
