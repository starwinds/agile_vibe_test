from pydantic import BaseModel, SecretStr
from vectordb_bench.backend.clients import DBConfig, DBCaseConfig, IndexType, MetricType

class ValkeyDBConfig(DBConfig):
    host: str = "127.0.0.1"
    port: int = 6379
    password: SecretStr | None = None

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "password": self.password.get_secret_value() if self.password else None,
        }

class ValkeyDBCaseConfig(BaseModel, DBCaseConfig):
    index_name: str = "vdbbench_idx"
    prefix: str = "doc:"
    M: int = 16
    EF_CONSTRUCTION: int = 200
    EF_RUNTIME: int = 10
    distance_metric: MetricType = MetricType.COSINE

    def index_param(self) -> dict:
        return {
            "M": self.M,
            "EF_CONSTRUCTION": self.EF_CONSTRUCTION,
            "EF_RUNTIME": self.EF_RUNTIME,
            "distance_metric": self.distance_metric.value,
        }

    def search_param(self) -> dict:
        return {
            "EF_RUNTIME": self.EF_RUNTIME,
        }
