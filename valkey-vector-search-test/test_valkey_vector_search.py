#!/usr/bin/env python3
"""
Valkey Vector Search 기능 테스트 스크립트

이 스크립트는 Valkey-Search 모듈의 벡터 검색 기능을 테스트합니다.
"""

import numpy as np
from valkey import Valkey
from typing import List, Dict, Any


class ValkeyVectorSearchTester:
    """Valkey Vector Search 테스트 클래스"""
    
    def __init__(self, host: str = "localhost", port: int = 6379):
        """
        Args:
            host: Valkey 서버 호스트
            port: Valkey 서버 포트
        """
        self.client = Valkey(host=host, port=port, decode_responses=True)
        self.index_name = "vector_test_idx"
        
    def test_connection(self) -> bool:
        """Valkey 서버 연결 테스트"""
        try:
            response = self.client.ping()
            print(f"✓ Valkey 서버 연결 성공: {response}")
            return True
        except Exception as e:
            print(f"✗ Valkey 서버 연결 실패: {e}")
            return False
    
    def check_modules(self) -> Dict[str, Any]:
        """로드된 모듈 확인"""
        try:
            modules = self.client.execute_command("MODULE LIST")
            print(f"\n로드된 모듈:")
            for module in modules:
                print(f"  - {module}")
            return modules
        except Exception as e:
            print(f"✗ 모듈 확인 실패: {e}")
            return {}
    
    def create_vector_index(self, dimension: int = 128) -> bool:
        """벡터 인덱스 생성
        
        Args:
            dimension: 벡터 차원
        """
        try:
            # 기존 인덱스 삭제 (있는 경우)
            try:
                self.client.execute_command("FT.DROPINDEX", self.index_name)
                print(f"기존 인덱스 '{self.index_name}' 삭제됨")
            except:
                pass
            
            # 새 인덱스 생성
            # FT.CREATE {index_name} ON HASH PREFIX 1 {prefix} 
            # SCHEMA {field_name} VECTOR HNSW 6 TYPE FLOAT32 DIM {dimension} DISTANCE_METRIC COSINE
            cmd = [
                "FT.CREATE", self.index_name,
                "ON", "HASH",
                "PREFIX", "1", "vec:",
                "SCHEMA",
                "embedding", "VECTOR", "HNSW", "6",
                "TYPE", "FLOAT32",
                "DIM", str(dimension),
                "DISTANCE_METRIC", "COSINE"
            ]
            
            self.client.execute_command(*cmd)
            print(f"✓ 벡터 인덱스 '{self.index_name}' 생성 성공 (차원: {dimension})")
            return True
            
        except Exception as e:
            print(f"✗ 벡터 인덱스 생성 실패: {e}")
            return False
    
    def insert_vectors(self, num_vectors: int = 100, dimension: int = 128) -> bool:
        """랜덤 벡터 데이터 삽입
        
        Args:
            num_vectors: 삽입할 벡터 개수
            dimension: 벡터 차원
        """
        try:
            print(f"\n{num_vectors}개의 벡터 삽입 중...")
            
            for i in range(num_vectors):
                # 랜덤 벡터 생성 (정규화)
                vector = np.random.randn(dimension).astype(np.float32)
                vector = vector / np.linalg.norm(vector)
                
                # 벡터를 바이트로 변환
                vector_bytes = vector.tobytes()
                
                # Hash로 저장
                key = f"vec:{i}"
                self.client.hset(key, mapping={
                    "embedding": vector_bytes,
                    "id": str(i),
                    "category": f"cat_{i % 5}"  # 5개 카테고리로 분류
                })
                
                if (i + 1) % 20 == 0:
                    print(f"  {i + 1}/{num_vectors} 벡터 삽입 완료")
            
            print(f"✓ {num_vectors}개의 벡터 삽입 성공")
            return True
            
        except Exception as e:
            print(f"✗ 벡터 삽입 실패: {e}")
            return False
    
    def search_vectors(self, k: int = 10, dimension: int = 128) -> bool:
        """벡터 유사도 검색 테스트
        
        Args:
            k: 검색할 이웃 개수
            dimension: 벡터 차원
        """
        try:
            # 쿼리 벡터 생성
            query_vector = np.random.randn(dimension).astype(np.float32)
            query_vector = query_vector / np.linalg.norm(query_vector)
            query_bytes = query_vector.tobytes()
            
            # FT.SEARCH 명령 실행
            # FT.SEARCH {index} "*=>[KNN {k} @{field} $query_vec]" PARAMS 2 query_vec {vector_blob} DIALECT 2
            cmd = [
                "FT.SEARCH", self.index_name,
                f"*=>[KNN {k} @embedding $query_vec]",
                "PARAMS", "2", "query_vec", query_bytes,
                "DIALECT", "2",
                "RETURN", "2", "id", "category"
            ]
            
            results = self.client.execute_command(*cmd)
            
            print(f"\n✓ 벡터 검색 성공 (K={k})")
            print(f"  검색 결과 개수: {results[0]}")
            
            # 결과 출력
            if results[0] > 0:
                print("\n  상위 결과:")
                # results 형식: [total_count, key1, [field1, value1, ...], key2, [field2, value2, ...], ...]
                for i in range(1, min(6, len(results)), 2):
                    key = results[i]
                    fields = results[i + 1] if i + 1 < len(results) else []
                    print(f"    {i//2 + 1}. Key: {key}")
                    if fields:
                        for j in range(0, len(fields), 2):
                            field_name = fields[j]
                            field_value = fields[j + 1] if j + 1 < len(fields) else ""
                            print(f"       {field_name}: {field_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ 벡터 검색 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def hybrid_search(self, k: int = 10, dimension: int = 128, category: str = "cat_0") -> bool:
        """하이브리드 검색 테스트 (벡터 검색 + 필터링)
        
        Args:
            k: 검색할 이웃 개수
            dimension: 벡터 차원
            category: 필터링할 카테고리
        """
        try:
            # 쿼리 벡터 생성
            query_vector = np.random.randn(dimension).astype(np.float32)
            query_vector = query_vector / np.linalg.norm(query_vector)
            query_bytes = query_vector.tobytes()
            
            # 카테고리 필터와 함께 검색
            cmd = [
                "FT.SEARCH", self.index_name,
                f"@category:{{{category}}}=>[KNN {k} @embedding $query_vec]",
                "PARAMS", "2", "query_vec", query_bytes,
                "DIALECT", "2",
                "RETURN", "2", "id", "category"
            ]
            
            results = self.client.execute_command(*cmd)
            
            print(f"\n✓ 하이브리드 검색 성공 (K={k}, Category={category})")
            print(f"  검색 결과 개수: {results[0]}")
            
            return True
            
        except Exception as e:
            print(f"✗ 하이브리드 검색 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_index_info(self) -> bool:
        """인덱스 정보 조회"""
        try:
            info = self.client.execute_command("FT.INFO", self.index_name)
            print(f"\n인덱스 '{self.index_name}' 정보:")
            
            # 정보를 딕셔너리로 변환
            info_dict = {}
            for i in range(0, len(info), 2):
                key = info[i]
                value = info[i + 1] if i + 1 < len(info) else None
                info_dict[key] = value
                
            # 주요 정보 출력
            if 'num_docs' in info_dict:
                print(f"  문서 개수: {info_dict['num_docs']}")
            if 'num_terms' in info_dict:
                print(f"  용어 개수: {info_dict['num_terms']}")
            if 'num_records' in info_dict:
                print(f"  레코드 개수: {info_dict['num_records']}")
            
            return True
            
        except Exception as e:
            print(f"✗ 인덱스 정보 조회 실패: {e}")
            return False
    
    def cleanup(self) -> bool:
        """테스트 데이터 정리"""
        try:
            # 인덱스 삭제
            self.client.execute_command("FT.DROPINDEX", self.index_name)
            print(f"\n✓ 인덱스 '{self.index_name}' 삭제 완료")
            
            # 벡터 데이터 삭제
            keys = self.client.keys("vec:*")
            if keys:
                self.client.delete(*keys)
                print(f"✓ {len(keys)}개의 벡터 데이터 삭제 완료")
            
            return True
            
        except Exception as e:
            print(f"✗ 정리 실패: {e}")
            return False


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("Valkey Vector Search 기능 테스트")
    print("=" * 60)
    
    # 테스트 파라미터
    DIMENSION = 128
    NUM_VECTORS = 100
    K = 10
    
    tester = ValkeyVectorSearchTester(host="localhost", port=6379)
    
    # 1. 연결 테스트
    if not tester.test_connection():
        print("\n❌ Valkey 서버에 연결할 수 없습니다.")
        return
    
    # 2. 모듈 확인
    tester.check_modules()
    
    # 3. 벡터 인덱스 생성
    if not tester.create_vector_index(dimension=DIMENSION):
        print("\n❌ 벡터 인덱스 생성 실패")
        return
    
    # 4. 벡터 데이터 삽입
    if not tester.insert_vectors(num_vectors=NUM_VECTORS, dimension=DIMENSION):
        print("\n❌ 벡터 데이터 삽입 실패")
        return
    
    # 5. 인덱스 정보 확인
    tester.get_index_info()
    
    # 6. 벡터 검색 테스트
    if not tester.search_vectors(k=K, dimension=DIMENSION):
        print("\n❌ 벡터 검색 실패")
    
    # 7. 하이브리드 검색 테스트
    if not tester.hybrid_search(k=K, dimension=DIMENSION, category="cat_0"):
        print("\n❌ 하이브리드 검색 실패")
    
    # 8. 정리
    cleanup_choice = input("\n테스트 데이터를 삭제하시겠습니까? (y/n): ")
    if cleanup_choice.lower() == 'y':
        tester.cleanup()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
