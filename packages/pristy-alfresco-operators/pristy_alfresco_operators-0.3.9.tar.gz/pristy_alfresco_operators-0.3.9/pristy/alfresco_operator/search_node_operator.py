# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from airflow.models.baseoperator import BaseOperator


class AlfrescoSearchOperator(BaseOperator):
    """
    Simple operator that uses the Alfresco search API.
    TODO: add parameter to sort field
    """
    from requests import Response

    def __init__(
            self,
            *,
            query: str,
            http_conn_id: str = "alfresco_api",
            page_size: int = 3,
            max_items: int = 2000,
            **kwargs):
        super().__init__(**kwargs)

        from airflow.providers.http.hooks.http import HttpHook
        self.http_hook = HttpHook(method="POST", http_conn_id=http_conn_id)
        self.query = query
        self.page_size = page_size
        self.max_items = max_items

    def execute(self, context):
        self.log.debug(f"search query={self.query}")

        self.data = {
            "query": {
                "query": self.query,
            },
            "paging": {
                "maxItems": self.page_size,
                "skipCount": 0
            },
            "include": ["path", "aspectNames", "properties"],
            "sort": [{"type": "FIELD", "field": "cm:created", "ascending": False}]
        }

        results = self.fetch_results(self.query)

        self.log.debug("--search results--")
        for result in results:
            self.log.debug(result)

        return results

    def fetch_results(self, query):
        entries = []

        response = self.http_hook.run(
            endpoint="/alfresco/api/-default-/public/search/versions/1/search",
            json=self.data,
        )
        all_responses = [response]
        while len(all_responses) < self.max_items:
            next_page_params = self.paginate(response)
            if not next_page_params:
                break
            self.log.info(f"Load next page with skipCount={next_page_params['skipCount']}")
            self.data["paging"]["skipCount"] = next_page_params["skipCount"]

            if (len(all_responses) + self.page_size) > self.max_items:
                self.data["paging"]["maxItems"] = self.max_items - len(all_responses)

            response = self.http_hook.run(
                endpoint="/alfresco/api/-default-/public/search/versions/1/search",
                json=self.data,
            )
            all_responses.append(response)

        for raw_resp in all_responses:
            resp_json = raw_resp.json()
            for e in resp_json["list"]["entries"]:
                entries.append(e["entry"])

        return entries

    def paginate(self, response: Response) -> dict | None:
        content = response.json()

        pagination = content['list']['pagination']
        count = pagination['count']
        skip_count = pagination['skipCount'] + self.page_size
        max_items = pagination['maxItems']
        self.log.debug(f"Request Alfresco pagination {count}/{max_items} ")

        if pagination['hasMoreItems']:
            return {"skipCount": skip_count}
        return None
