# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.models.baseoperator import BaseOperator
from airflow.providers.apache.kafka.hooks.produce import KafkaProducerHook


def _load_schema() -> dict[str, Any]:
    from importlib import resources
    import json

    with resources.open_text("pristy.schema", "node_injector.schema.json") as schema_file:
        content = json.load(schema_file)
    return content


def _hash_key(node: dict) -> str:
    import hashlib
    path = node['path']['root'] + node['path']['short']
    hash_object = hashlib.sha1(path.encode("utf-8"))
    return hash_object.hexdigest()


def _json_dump(c):
    import json
    import base64

    if '__dag_param' not in c:
        return json.dumps(c)

    dag_param = c['__dag_param']
    if 'local_source_file' in dag_param:
        with open(dag_param['local_source_file'], 'rb') as f:
            file_content = f.read()
            encoded_content = base64.b64encode(file_content)
            c['source']['base64'] = encoded_content.decode('utf-8')
    del c['__dag_param']
    return json.dumps(c)


class PushToKafkaOperator(BaseOperator):
    """
    Push a node into kafka injector topic.
    First valid schema using jsonschema
    Finally update state for the node in local db

    :param source_key: specify key in source to update local db, defaults to 'uuid'

    """

    def __init__(
            self,
            *,
            nodes,
            table_name,
            source_key: str = "uuid",
            **kwargs):
        super().__init__(**kwargs)
        self.nodes = nodes
        self.table_name_local_db = table_name
        self.source_key = source_key

    def execute(self, context):
        from pristy.alfresco_operator.update_node_db import update_state_db
        import jsonschema
        import json

        if len(self.nodes) == 0:
            raise AirflowSkipException('No node to proceed')
        if isinstance(self.nodes, list):
            nodes_array = self.nodes
        else:
            nodes_array = [self.nodes]

        topic = Variable.get('kafka_export_topic')

        schema = _load_schema()

        kafka_hook = KafkaProducerHook(kafka_config_id="kafka_pristy")
        producer = kafka_hook.get_producer()
        follow = []
        for c in nodes_array:
            self.log.info(f"push {c['path']['short']}/{c['name']}")
            if '__dag_param' in c:
                local_db_id = c['__dag_param']['local_db_id']
            else:
                local_db_id = c['source']['uuid']

            node_json = _json_dump(c)
            try:
                jsonschema.validate(json.loads(node_json), schema=schema)
            except jsonschema.ValidationError as ex:
                raise RuntimeError(f"Fail to validate export. Original error {type(ex).__name__}: {ex}")
            try:
                producer.produce(
                    topic,
                    key=_hash_key(c),
                    value=node_json,
                    on_delivery=self.acked,
                    headers={
                        "type": c['type'],
                        "path": c['path']['short'],
                        "name": c['name'],
                    }
                )
                follow.append(local_db_id)
                update_state_db(local_db_id, "sending", self.table_name_local_db, self.source_key)
            except BufferError:
                self.log.warning(
                    f'Local producer queue is full ({len(producer)} messages awaiting delivery): try again')

        still_in_queue = producer.flush(timeout=10)
        if still_in_queue > 0:
            for d in follow:
                update_state_db(d, "fail", self.table_name_local_db, self.source_key)
            raise RuntimeError(f"Message still in queue : {still_in_queue}")

        for d in follow:
            update_state_db(d, "success", self.table_name_local_db, self.source_key)

    def acked(self, err, msg):
        if err is not None:
            self.log.error("Failed to deliver message: %s", err)
        else:
            self.log.debug(
                "Produced record to topic %s, partition [%s] @ offset %s",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )
