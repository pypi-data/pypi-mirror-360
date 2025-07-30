from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Sequence
from urllib.parse import urljoin, urlparse

import httpx
from duneflow.models import RawCell, RawLink, RawTable, RawTableMetadata
from duneflow.typing import URL
from libactor.actor import Actor
from libactor.cache import BackendFactory, IdentObj, cache
from loguru import logger
from rsoup.core import ContextExtractor, Document, Table, TableExtractor
from tqdm import tqdm


@dataclass
class TableScraperArgs:
    max_num_hop: int = field(
        default=0,
        metadata={
            "help": "Max number of hops to follow. 0 means we do not follow any links, 1 means we follow only the links on the page, etc."
        },
    )
    max_num_links: int = field(
        default=1000, metadata={"help": "Max number of links to follow."}
    )
    only_follow_same_domain: bool = field(
        default=True,
        metadata={"help": "Whether to only follow links on the same domain."},
    )


class TableScraperActor(Actor[TableScraperArgs]):
    VERSION = 102

    def __init__(
        self, params: TableScraperArgs, dep_actors: Optional[Sequence[Actor]] = None
    ):
        super().__init__(params, dep_actors=dep_actors)
        self.table_extractor = TableExtractor(
            context_extractor=ContextExtractor(), html_error_forgiveness=True
        )

    @cache(
        backend=BackendFactory.actor.sqlite.pickle(mem_persist=True),
    )
    def forward(self, url: URL) -> Sequence[IdentObj[RawTable]]:
        queue = deque([(0, url)])
        output = []
        visited_urls = {url}

        domain = urlparse(url).netloc

        with tqdm(desc="Scraping", total=len(visited_urls)) as pbar:
            while len(queue) > 0:
                hop, url = queue.popleft()
                pbar.total = len(visited_urls)
                pbar.update(1)

                # extract HTML from the current URL
                html = self.get_html(url)

                # extract tables
                output += self.extract_table(url)

                # do not follow links if we have reached the max number of hops or the max number of links
                if (
                    hop >= self.params.max_num_hop
                    or len(visited_urls) >= self.params.max_num_links
                ):
                    continue
                doc = Document(url, html)
                for a in doc.select("a"):
                    href = a.attr("href")
                    if href.startswith("#"):
                        # local url
                        continue

                    if href.startswith("/"):
                        # domain-relative url
                        href = f"{domain}{href}"
                    elif not (href.startswith("http") or href.startswith("https")):
                        if url.endswith("/"):
                            href = f"{url}{href}"
                        else:
                            href = f"{url}/{href}"

                    if self.params.only_follow_same_domain:
                        if urlparse(href).netloc != domain:
                            continue

                    if href in visited_urls:
                        continue

                    visited_urls.add(href)
                    queue.append((hop + 1, href))

                    if len(visited_urls) >= self.params.max_num_links:
                        break

        return output

    @cache(
        backend=BackendFactory.actor.sqlite.pickle(mem_persist=True),
    )
    def get_html(self, url: URL) -> str:
        return httpx.get(url, follow_redirects=True).raise_for_status().text

    def extract_table(self, url: URL) -> Sequence[IdentObj[RawTable]]:
        try:
            tables = self.table_extractor.extract(
                url,
                self.get_html(url),
                auto_span=True,
                auto_pad=True,
                extract_context=True,
            )
        except Exception as e:
            logger.error(
                "Error while extracting tables from webpage: {}",
                url,
            )
            raise
        return [
            IdentObj(
                key=tbl.id,
                value=_rsoup_table_to_raw_table(tbl),
            )
            for tbl in tables
        ]


def _rsoup_table_to_raw_table(tbl: Table) -> RawTable:
    nrows, ncols = tbl.shape()
    data: list[list[RawCell]] = [
        [RawCell() for _ in range(ncols)] for _ in range(nrows)
    ]

    for ri in range(nrows):
        row = tbl.get_row(ri)
        for ci in range(ncols):
            cell = row.get_cell(ci)
            raw_cell = data[ri][ci]

            links: list[RawLink] = []
            value = cell.value
            for eid in value.iter_element_id():
                if value.get_element_tag_by_id(eid) == "a":
                    href = value.get_element_attr_by_id(eid, "href")
                    if href is not None:
                        el = value.get_element_by_id(eid)
                        link = RawLink(
                            start=el.start,
                            end=el.end,
                            url=_norm_url(tbl.url, href),
                        )
                        links.append(link)

            raw_cell.value = value.text
            raw_cell.metadata["colspan"] = cell.colspan
            raw_cell.metadata["rowspan"] = cell.rowspan
            raw_cell.metadata["is_header"] = cell.is_header
            raw_cell.metadata["links"] = links

    return RawTable(
        id=tbl.id,
        data=data,
        context=tbl.context,
        metadata=RawTableMetadata(
            url=tbl.url,
            caption=tbl.caption,
        ),
    )


def _norm_url(page_url: str, url: str) -> str:
    result = urlparse(url)
    if result.netloc != "" and result.scheme != "":
        return url

    # urljoin works for Domain-relative URLs
    # e.g. (https://example.com/resource/foo.html, bar.html) => https://example.com/resource/bar.html
    # e.g. (https://example.com/resource/foo.html, /bar.html) => https://example.com/bar.html
    return urljoin(page_url, url)
