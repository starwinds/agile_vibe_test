# Valkey Docker 이미지 비교 검토

## 이미지 종류

### 1. valkey/valkey-bundle
- **용도**: Valkey 서버와 모든 모듈이 포함된 완전한 번들 이미지
- **포함 모듈**:
  - Valkey 서버 (core)
  - Search 모듈 (벡터 검색 포함)
  - JSON 모듈
  - Bloom Filter 모듈
  - LDAP 모듈
- **특징**:
  - 모든 모듈이 사전 로드됨
  - 별도 설정 없이 바로 벡터 검색 사용 가능
  - 프로덕션 및 벤치마크에 적합
- **권장 사용**: ✅ **벤치마크 및 프로덕션 환경**

### 2. valkey/valkey-extension
- **용도**: 확장 모듈만 포함 (서버가 아님)
- **포함 모듈**: 확장 기능 모듈들
- **특징**:
  - Valkey 서버가 포함되지 않음
  - 모듈만 제공
  - 별도로 Valkey 서버가 필요
- **권장 사용**: ❌ 벤치마크에는 부적합 (서버가 없음)

## 결론

**valkey/valkey-bundle**을 사용하는 것이 적합합니다:
1. 벡터 검색 모듈이 이미 포함되어 있음
2. 별도 설정 없이 바로 사용 가능
3. 현재 벤치마크 가이드에서도 사용 중
4. 모든 필요한 모듈이 사전 로드됨

## 사용 예시

```bash
# Dockerfile에서 사용
FROM valkey/valkey-bundle:latest

# docker-compose에서 사용
services:
  valkey:
    image: valkey/valkey-bundle:latest
    ports:
      - "6379:6379"
```

