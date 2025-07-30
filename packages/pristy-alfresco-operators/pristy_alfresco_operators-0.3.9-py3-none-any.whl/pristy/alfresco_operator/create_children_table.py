# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator


class CreateChildrenTableOperator(BaseOperator):
    """
    Simple operator that query children api.
    """

    def __init__(self, *arg, **kwargs):
        super().__init__(**kwargs)

    def execute(self, context):
        postgres_hook = PostgresHook(postgres_conn_id="local_pg")
        conn = postgres_hook.get_conn()
        cur = conn.cursor()
        # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        cur.execute("DROP TABLE IF EXISTS export_alfresco_folder_children")
        cur.execute(
            """
            CREATE TABLE export_alfresco_folder_children (
            id SERIAL PRIMARY KEY,
            parentid varchar,
            uuid varchar,
            state varchar DEFAULT 'new'
            )
            """
        )
        conn.commit()
