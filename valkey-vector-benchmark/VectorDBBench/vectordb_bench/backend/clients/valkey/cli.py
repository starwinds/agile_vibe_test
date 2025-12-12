from typing import Annotated, TypedDict, Unpack, List
import click
from pydantic import SecretStr

from ....cli.cli import (
    CommonTypedDict,
    HNSWFlavor2,
    cli,
    click_parameter_decorators_from_typed_dict,
    run,
)
from .. import DB
from .config import ValkeyDBCaseConfig, DeploymentType


class ValkeyTypedDict(TypedDict):
    host: Annotated[str, click.option("--host", type=str, default="127.0.0.1", help="Db host")]
    port: Annotated[int, click.option("--port", type=int, default=6379, help="Db Port")]
    password: Annotated[str, click.option("--password", type=str, help="Db password")]
    deployment_type: Annotated[
        str,
        click.option(
            "--deployment-type",
            type=click.Choice([t.value for t in DeploymentType]),
            default=DeploymentType.STANDALONE.value,
            help="Deployment type: STANDALONE, CLUSTER, SENTINEL",
        ),
    ]
    nodes: Annotated[
        str,
        click.option(
            "--nodes",
            type=str,
            help="Comma separated list of host:port for Cluster or Sentinel",
        ),
    ]
    service_name: Annotated[
        str,
        click.option(
            "--service-name",
            type=str,
            help="Service name for Sentinel",
        ),
    ]


class ValkeyHNSWTypedDict(CommonTypedDict, ValkeyTypedDict, HNSWFlavor2): ...


@cli.command()
@click_parameter_decorators_from_typed_dict(ValkeyHNSWTypedDict)
def Valkey(**parameters: Unpack[ValkeyHNSWTypedDict]):
    from .config import ValkeyDBConfig

    nodes_list = None
    if parameters.get("nodes"):
        nodes_list = [n.strip() for n in parameters["nodes"].split(",")]

    run(
        db=DB.Valkey,
        db_config=ValkeyDBConfig(
            db_label=parameters["db_label"],
            host=parameters["host"],
            port=parameters["port"],
            password=SecretStr(parameters["password"]) if parameters.get("password") else None,
            deployment_type=DeploymentType(parameters["deployment_type"]),
            nodes=nodes_list,
            service_name=parameters.get("service_name"),
        ),
        db_case_config=ValkeyDBCaseConfig(
            M=parameters["m"],
            EF_CONSTRUCTION=parameters["ef_construction"],
            EF_RUNTIME=parameters["ef_runtime"],
        ),
        **parameters,
    )
