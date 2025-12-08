import logging
import time
from typing import Any, Iterable, List
from contextlib import contextmanager
import valkey
from valkey.commands.search.field import TagField, NumericField, VectorField
from valkey.commands.search.indexDefinition import IndexDefinition, IndexType
from valkey.commands.search.query import Query
import numpy as np

from ...utils import time_it
from ..api import VectorDB, DBCaseConfig
from .config import ValkeyDBConfig, ValkeyDBCaseConfig

log = logging.getLogger(__name__)

class ValkeyClient(VectorDB):
    def __init__(
        self,
        dim: int,
        db_config: ValkeyDBConfig,
        db_case_config: ValkeyDBCaseConfig,
        drop_old: bool = False,
        **kwargs,
    ):
        self.dim = dim
        self.db_config = db_config
        self.case_config = db_case_config
        self.index_name = db_case_config.index_name
        self.prefix = db_case_config.prefix
        
        # Initialize connection for setup
        self.client = valkey.Valkey(
            host=db_config.host,
            port=db_config.port,
            password=db_config.password.get_secret_value() if db_config.password else None,
            decode_responses=True
        )

        if drop_old:
            self.cleanup()
            self._init_index()
            
        self.client.close()
        self.client = None

    @contextmanager
    def init(self) -> None:
        self.client = valkey.Valkey(
            host=self.db_config.host,
            port=self.db_config.port,
            password=self.db_config.password.get_secret_value() if self.db_config.password else None,
            decode_responses=True
        )
        yield
        self.client.close()
        self.client = None

    def _init_index(self):
        try:
            self.client.ft(self.index_name).info()
            log.info(f"Index {self.index_name} already exists.")
            return
        except Exception:
            pass

        schema = (
            TagField("id"),
            NumericField("metadata"),
            VectorField(
                "vector",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.dim,
                    "DISTANCE_METRIC": self.case_config.distance_metric.value,
                    "M": self.case_config.M,
                    "EF_CONSTRUCTION": self.case_config.EF_CONSTRUCTION,
                }
            )
        )
        
        definition = IndexDefinition(prefix=[self.prefix], index_type=IndexType.HASH)
        
        self.client.ft(self.index_name).create_index(
            schema,
            definition=definition
        )
        log.info(f"Index {self.index_name} created.")

    def optimize(self, data_size: int | None = None):
        pass


    def insert_embeddings(
        self,
        embeddings: list[list[float]],
        metadata: list[int],
        labels_data: list[str] | None = None,
        **kwargs,
    ) -> tuple[int, Exception]:
        pipe = self.client.pipeline(transaction=False)
        count = 0
        try:
            for i, vector in enumerate(embeddings):
                id_val = metadata[i]
                key = f"{self.prefix}{id_val}"
                
                import struct
                vector_bytes = struct.pack(f'{len(vector)}f', *vector)
                
                pipe.hset(key, mapping={
                    "id": str(id_val),
                    "metadata": id_val, # Assuming metadata is int and used for filtering
                    "vector": vector_bytes
                })
                
                count += 1
                if count % 1000 == 0:
                    pipe.execute()
                    pipe = self.client.pipeline(transaction=False)
            
            if count % 1000 != 0:
                pipe.execute()
                
            return count, None
        except Exception as e:
            return count, e


    def search_embedding(
        self,
        query: list[float],
        k: int = 100,
        filters: dict | None = None,
        timeout: int | None = None,
    ) -> List[int]:
        import struct
        query_bytes = struct.pack(f'{len(query)}f', *query)
        
        # Basic query
        q_str = f"*=>[KNN {k} @vector $vec_param AS vector_score]"
        
        # Handle filters
        if filters:
            id_value = filters.get("id")
            metadata_value = filters.get("metadata")
            
            if id_value is not None and metadata_value is not None:
                q_str = f"(@metadata:[{metadata_value} +inf] @id:{{{id_value}}})=>[KNN {k} @vector $vec_param AS vector_score]"
            elif id_value is not None:
                q_str = f"@id:{{{id_value}}}=>[KNN {k} @vector $vec_param AS vector_score]"
            elif metadata_value is not None:
                q_str = f"@metadata:[{metadata_value} +inf]=>[KNN {k} @vector $vec_param AS vector_score]"

        q = Query(q_str)\
            .sort_by("vector_score")\
            .return_fields("id")\
            .dialect(2)
        
        params = {"vec_param": query_bytes}
        
        res = self.client.ft(self.index_name).search(q, query_params=params)
        
        # Parse results
        # We stored "id" field as string of int
        ids = [int(doc.id.split(self.prefix)[1]) for doc in res.docs]
        return ids

    def cleanup(self):
        try:
            self.client.ft(self.index_name).dropindex(delete_documents=True)
            log.info(f"Index {self.index_name} and documents deleted.")
        except Exception as e:
            log.warning(f"Failed to cleanup index {self.index_name}: {e}")
