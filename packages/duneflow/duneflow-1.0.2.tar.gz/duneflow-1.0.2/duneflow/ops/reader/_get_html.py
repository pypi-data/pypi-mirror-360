from __future__ import annotations

from functools import partial
from hashlib import sha256

import httpx
from duneflow.typing import URL
from libactor.actor import Actor
from libactor.cache import BackendFactory, IdentObj, cache
from libactor.misc import NoParams


@cache(
    backend=BackendFactory.func.sqlite.pickle(
        dbdir=partial(
            BackendFactory.func.workdir, func="duneflow.ops.get_html", version=100
        ),
        mem_persist=True,
    ),
)
def get_html(url: URL) -> IdentObj[str]:
    html = httpx.get(url, follow_redirects=True).raise_for_status().text
    key = sha256(html.encode()).hexdigest()
    return IdentObj(key, html)


# class GetHtmlActor(Actor[NoParams]):
#     @cache(
#         backend=BackendFactory.actor.sqlite.pickle(
#             mem_persist=True,
#         )
#     )
#     def forward(self, url: URL) -> IdentObj[str]:
#         html = httpx.get(url, follow_redirects=True).raise_for_status().text
#         key = sha256(html.encode()).hexdigest()
#         return IdentObj(key, html)
