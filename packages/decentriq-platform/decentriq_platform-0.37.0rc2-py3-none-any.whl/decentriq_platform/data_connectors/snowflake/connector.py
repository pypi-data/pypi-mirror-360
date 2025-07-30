from __future__ import annotations

from ...analytics.node_definitions import NodeDefinition
from ...analytics.high_level_node import ComputationNode
from ...session import Session
from typing import Dict
from decentriq_dcr_compiler._schemas.data_science_data_room import (
    SnowflakeConfig,
)
from typing_extensions import Self


class SnowflakeImportConnectorDefinition(NodeDefinition):
    def __init__(
        self,
        name: str,
        warehouse_name: str,
        database_name: str,
        schema_name: str,
        table_name: str,
        stage_name: str,
        credentials_dependency: str,
    ) -> None:
        """
        Initialise a `SnowflakeImportConnectorDefinition`.
        This class is used in order to construct SnowflakeImportConnectors.

        **Parameters**:
        - `name`: Name of the `SnowflakeImportConnectorDefinition`.
        - `warehouse_name`: Name of the warehouse to be used.
        - `database_name`: Name of the database to be used.
        - `schema_name`: Name of the schema to be used.
        - `table_name`: Name of the table where data is imported from.
        - `credentials_dependency`: Name of the credentials node.
        """
        super().__init__(name, id=name)
        self.warehouse_name = warehouse_name
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.stage_name = stage_name
        self.credentials_dependency = credentials_dependency
        self.specification_id = "decentriq.python-ml-worker-32-64"

    def _get_high_level_representation(self) -> Dict[str, str]:
        """
        Retrieve the high level representation of the `SnowflakeImportConnectorDefinition`.
        """
        return {
            "id": self.id,
            "name": self.name,
            "kind": {
                "computation": {
                    "kind": {
                        "importConnector": {
                            "credentialsDependency": self.credentials_dependency,
                            "kind": {
                                "snowflake": {
                                    "databaseName": self.database_name,
                                    "schemaName": self.schema_name,
                                    "stageName": self.stage_name,
                                    "tableName": self.table_name,
                                    "warehouseName": self.warehouse_name,
                                }
                            },
                            "specificationId": self.specification_id,
                        },
                    },
                }
            },
        }

    def build(
        self,
        dcr_id: str,
        node_definition: NodeDefinition,
        client: Client,
        session: Session,
    ) -> SnowflakeImportConnector:
        """
        Construct a SnowflakeImportConnector from the Node Definition.

        **Parameters**:
        - `dcr_id`: ID of the DCR the node is a member of.
        - `node_definition`: Definition of the Import Connector Node.
        - `client`: A `Client` object which can be used to perform operations such as uploading data
            and retrieving computation results.
        - `session`: The session with which to communicate with the enclave.
        """
        return SnowflakeImportConnector(
            name=self.name,
            dcr_id=dcr_id,
            client=client,
            session=session,
            connector_definition=node_definition,
        )

    @property
    def required_workers(self):
        return [self.specification_id]

    @classmethod
    def _from_high_level(
        cls,
        name: str,
        config: SnowflakeConfig,
        credentials_dependency: str,
    ) -> Self:
        """
        Instantiate a `SnowflakeImportConnectorDefinition` from its high level representation.

        **Parameters**:
        - `name`: Name of the `SnowflakeImportConnectorDefinition`.
        - `config`: Pydantic model of the `SnowflakeConfig`.
        - `credentials_dependency`: Name of the credentials dependency node.
        """
        return cls(
            name=name,
            warehouse_name=config.warehouseName,
            database_name=config.databaseName,
            schema_name=config.schemaName,
            table_name=config.tableName,
            stage_name=config.stageName,
            credentials_dependency=credentials_dependency,
        )


class SnowflakeImportConnector(ComputationNode):
    """
    A SnowflakeImportConnector which can import data from Snowflake.
    """

    def __init__(
        self,
        name: str,
        dcr_id: str,
        client: Client,
        session: Session,
        connector_definition: SnowflakeImportConnectorDefinition,
    ) -> None:
        """
        Initialise a `SnowflakeImportConnector`.

        **Parameters**:
        - `name`: Name of the `SnowflakeImportConnector`.
        - `dcr_id`: ID of the DCR the connector is a member of.
        - `client`: A `Client` object which can be used to perform operations such as uploading data
            and retrieving computation results.
        - `session`: The session with which to communicate with the enclave.
        - `connector_definition`: Definition of the Snowflake import connector.
        """
        super().__init__(
            name=name,
            client=client,
            session=session,
            dcr_id=dcr_id,
            id=name,
            definition=connector_definition,
        )
        self.definition = connector_definition

    def _get_computation_id(self) -> str:
        """
        Retrieve the ID of the node corresponding to the connector.
        """
        return f"{self.id}_container"
