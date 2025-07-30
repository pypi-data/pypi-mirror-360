from __future__ import annotations

from pathlib import Path

from rdflib import Graph


def write_ttl(
    text: str, outdir: Path, filename: str = "data", normalize: bool = False
) -> str:
    """Write a string to a file"""
    if normalize:
        g = Graph()
        g.parse(data=text, format="turtle")
        text = g.serialize(format="turtle")

    (outdir / (filename + ".ttl")).write_text(text)
    return text
