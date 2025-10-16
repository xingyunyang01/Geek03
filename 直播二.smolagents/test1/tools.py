import json
import os

import requests
from smolagents import Tool
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class BoChaSearchTool(Tool):
    """BoCha search tool that performs Bocha searches.
    It uses the BoCha Search API.

    This tool implements a rate limiting mechanism to ensure compliance with API usage policies.
    By default, it limits requests to 1 query per second.

    Args:
        endpoint (`str`): API endpoint URL. Defaults to BoCha Search API.
        api_key (`str`): API key for authentication.
        api_key_name (`str`): Environment variable name containing the API key. Defaults to "BOCHA_API_KEY".
        headers (`dict`, *optional*): Headers for API requests.
        page (`int`, *optional*): Page number. Defaults to 1.
        pagesize (`int`, *optional*): Page size. Defaults to 5.
        rate_limit (`float`, default `1.0`): Maximum queries per second. Set to `None` to disable rate limiting.

    Examples:
        ```python
        >>> from smolagents import BoChaSearchTool
        >>> web_search_tool = BoChaSearchTool(rate_limit=50.0)
        >>> results = web_search_tool("Hugging Face")
        >>> print(results)
        ```
    """

    name = "web_search"
    description = "Performs a web search for a query and returns a string of the top search results formatted as markdown with titles, URLs, and descriptions."
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "string"

    def __init__(
        self,
        api_key: str = "",
        api_key_name: str = "",
        headers: dict = None,
        page: int = 1,
        pagesize: int = 5,
        rate_limit: float | None = 1.0,
    ):

        super().__init__()
        self.endpoint = "https://api.bochaai.com/v1/web-search"
        self.api_key_name = api_key_name or "BOCHA_API_KEY"
        self.api_key = api_key or os.environ.get(self.api_key_name)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.page = page
        self.pagesize = pagesize
        self.rate_limit = rate_limit
        self._min_interval = 1.0 / rate_limit if rate_limit else 0.0
        self._last_request_time = 0.0

    def _enforce_rate_limit(self) -> None:
        import time

        # No rate limit enforced
        if not self.rate_limit:
            return

        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def forward(self, query: str) -> str:
        import requests

        self._enforce_rate_limit()
        data = {
            "query":query,
            "summary":True,
            "count":self.pagesize,
            "page":self.page
        }
        response = requests.post(self.endpoint, headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        search_ret = response.json()
        return self.bocha_for_list(search_ret)

    def bocha_for_list(self, search_ret: dict):
        data = search_ret["data"]
        pages = data["webPages"]["value"]
        ret=[]
        for page in pages:
            ret.append({"title":page["name"],"summary":page["summary"],"url":page["url"]})
        return ret