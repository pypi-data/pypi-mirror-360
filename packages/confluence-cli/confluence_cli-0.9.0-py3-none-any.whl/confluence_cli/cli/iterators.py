import logging
from typing import Generator, Optional
from urllib.parse import urlparse, parse_qs

from confluence_cli.cli import ConfluenceWrapper


logger = logging.getLogger(__name__)


class CloudCQLResultIterator(object):
    """
    Pagination changes in cloud from feb-2020
    See https://community.developer.atlassian.com/t/upcoming-changes-to-modernize-search-rest-apis/37746"""

    def __init__(
        self, confluence: ConfluenceWrapper, cql: str, expand: str, page_size: int
    ):
        """Create a CQLPaginator instance with cql data

        Args:
            confluence (ConfluenceWrapper): [description]
            cql (str): [cql string]
            expand (str): [expand]
            page_size (int): [page size]
        """

        self.confluence = confluence
        self.cql = cql
        self.expand = expand
        self.page_size = page_size
        self.next_params = None

    def __iter__(self):
        return self._get_results()

    def _get_results(self) -> Generator:
        resp = self.confluence.cql(
            cql=self.cql, expand=self.expand, limit=self.page_size
        )
        contents = resp.get("results")
        for content in contents:
            yield content

        next_params = self._get_params_from_next(resp.get("_links").get("next"))
        while next_params:
            resp = self.confluence.get("rest/api/search", params=next_params)
            contents = resp.get("results")
            for content in contents:
                yield content
            next_params = self._get_params_from_next(resp.get("_links").get("next"))

    @staticmethod
    def _get_params_from_next(url: str) -> Optional[dict]:
        if not url:
            return None
        query = urlparse(url).query
        dl = parse_qs(query)
        d = {key: dl.get(key, [""])[0] for key in dl.keys()}
        return d


class CQLResultIterator(object):
    """Use like:

    result_pages = []
    for page in cql_res_iter:
        pages.append(page)
    """

    def __init__(
        self, confluence: ConfluenceWrapper, cql: str, expand: str, page_size: int
    ):
        """Create a CQLResultIterator instance with cql data

        Args:
            confluence (ConfluenceWrapper): [description]
            cql (str): [cql string]
            expand (str): [expand]
            page_size (int): [page size]
        """
        self.confluence = confluence
        self.cql = cql
        self.expand = expand
        self.page_size = page_size

    def __iter__(self):
        return self._get_results()

    def _get_results(self):
        start = 0
        total_size = 1
        while start < total_size:
            contents = self.confluence.cql(
                cql=self.cql, start=start, expand=self.expand, limit=self.page_size
            )
            if contents:
                # confluence wrapper sets totalSize key inside content
                # (see confluence wrapper cql method)
                if isinstance(contents, dict):
                    total_size = int(contents.get("totalSize"))
                    content_lst = contents.get("results")
                else:
                    total_size = int(contents[0].get("totalSize"))
                    content_lst = contents
            else:
                logger.info("Total Size cql: 0")
                self.total_size = 0
                return

            for content in content_lst:
                yield content
            start = start + self.page_size
