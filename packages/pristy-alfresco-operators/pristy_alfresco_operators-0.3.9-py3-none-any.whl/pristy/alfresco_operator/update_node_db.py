# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

def update_node_state_db(node: object, state: str):
    update_state_db(node['id'], state)


def update_state_db(
        child_id: str,
        state: str,
        table_name: str = "export_alfresco_folder_children",
        source_key: str = "uuid"):
    import logging
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    logger = logging.getLogger("airflow.task")
    logger.debug(f"Set node {child_id} to {state}")
    postgres_hook = PostgresHook(postgres_conn_id="local_pg")
    conn = postgres_hook.get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table_name} SET state = '{state}' WHERE {source_key} = '{child_id}'")
    conn.commit()

    logger.debug("commit")
