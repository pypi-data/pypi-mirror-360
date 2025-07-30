# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from airflow.exceptions import AirflowSkipException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator


class SaveFolderToDbOperator(BaseOperator):
    """
    Simple operator that query children api.
    :param parent_node_id: (required) parent node id
    :param node_id: (required)  node id to save
    """

    def __init__(self, *, child, **kwargs):
        super().__init__(**kwargs)
        self.child = child

    def execute(self, context):
        if len(self.child) == 0:
            raise AirflowSkipException('No child to proceed')

        postgres_hook = PostgresHook(postgres_conn_id="local_pg")
        conn = postgres_hook.get_conn()
        cur = conn.cursor()

        insert_rows = []
        for c in self.child:
            if not c['isFolder']:
                continue
            self.log.debug(f"save {c['parentId']} -> {c['id']} ({c['name']})")
            insert_rows.append((c['parentId'], c['id']))

            cur.execute(
                f"UPDATE export_alfresco_folder_children SET state = 'success' WHERE uuid = '{c['parentId']}'")

        if len(insert_rows) == 0:
            conn.rollback()
            raise AirflowSkipException('No file transformed, mark as skip')

        # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        cur.executemany(
            """
            INSERT INTO export_alfresco_folder_children (parentid, uuid, state)
            VALUES ( %s, %s, 'new')
            """,
            insert_rows
        )
        conn.commit()
