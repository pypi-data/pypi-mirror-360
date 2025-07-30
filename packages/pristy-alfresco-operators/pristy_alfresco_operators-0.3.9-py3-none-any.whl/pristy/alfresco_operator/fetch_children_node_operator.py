# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from airflow.models.baseoperator import BaseOperator
from airflow.models.expandinput import MappedArgument
from airflow.providers.http.hooks.http import HttpHook
from airflow.utils.helpers import merge_dicts
from requests import Response


class AlfrescoFetchChildrenOperator(BaseOperator):
    """
    Simple operator that load all children nodes from one or many folders.
    :param parent_node_id: (required) parent node id
    """

    def __init__(
            self,
            *,
            folders,
            page_size: int = 3,
            max_items: int = 2000,
            **kwargs):
        super().__init__(**kwargs)
        self.max_items = max_items

        self.http_hook = HttpHook(method="GET", http_conn_id="alfresco_api", )
        self.data = {"skipCount": 0, "maxItems": page_size, "orderBy": "createdAt",
                     "include": "path,aspectNames,properties"}
        self.folders = folders
        self.page_size = page_size

    def execute(self, context):
        self.log.debug(f"get_children type={self.folders}")

        f_children = []
        if isinstance(self.folders, MappedArgument):
            parent_id = self.folders.resolve(context)
            f_children.extend(self.fetch_children(parent_id))
        else:
            f_children.extend(self.fetch_children(self.folders))

        self.log.debug("--children--")
        for c in f_children:
            self.log.debug(c)

        return f_children

    def fetch_children(self, parent_id):
        from pristy.alfresco_operator.update_node_db import update_state_db

        self.log.info(f"fetch_children pid={parent_id}")
        response = self.http_hook.run(
            endpoint=f"/alfresco/api/-default-/public/alfresco/versions/1/nodes/{parent_id}/children",
            data=self.data,
        )
        all_responses = [response]
        while len(all_responses) < self.max_items:
            next_page_params = self.paginate(response)
            if not next_page_params:
                break
            self.log.info(f"Load next page {next_page_params.get("data")}")

            if (len(all_responses) + self.page_size) > self.max_items:
                self.data["paging"]["maxItems"] = self.max_items - len(all_responses)

            response = self.http_hook.run(
                endpoint=f"/alfresco/api/-default-/public/alfresco/versions/1/nodes/{parent_id}/children",
                data=merge_dicts(self.data, next_page_params.get("data")),
            )
            all_responses.append(response)

        entries = []
        for raw_resp in all_responses:
            resp_json = raw_resp.json()
            for e in resp_json["list"]["entries"]:
                entries.append(e["entry"])

        update_state_db(parent_id, "success")
        return entries

    def paginate(self, response: Response) -> dict | None:
        content = response.json()

        pagination: dict = content['list']['pagination']
        count: int = pagination['count']
        skip_count = pagination['skipCount'] + self.page_size
        max_items: int = pagination['maxItems']
        self.log.debug(f"Request Alfresco pagination {count}/{max_items} ")

        if pagination['hasMoreItems']:
            return dict(data={"skipCount": skip_count})
        return None
