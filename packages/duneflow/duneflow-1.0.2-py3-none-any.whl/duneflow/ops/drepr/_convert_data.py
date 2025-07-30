from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

import orjson
from drepr.main import DRepr, OutputFormat, convert
from drepr.models.prelude import (
    DRepr,
    OutputFormat,
    ResourceDataObject,
    ResourceDataString,
)
from duneflow.ops.drepr._make_drepr_model import create_drepr_model
from kgdata.models import Ontology
from libactor.cache import IdentObj
from sm.dataset import SemanticModel
from sm.inputs.table import ColumnBasedTable


def convert_data_from_drepr(
    table: ColumnBasedTable, drepr: DRepr, format: OutputFormat = OutputFormat.TTL
) -> str:
    nrows, ncols = table.shape()
    rows = [[table.columns[ci].clean_name for ci in range(ncols)]]
    rows.extend(
        ([table.columns[ci].values[ri] for ci in range(ncols)] for ri in range(nrows))
    )
    resources = {
        "table": ResourceDataObject(rows),
        # "entity": get_entity_resource(
        #     self.appcfg, self.namespace, table, rows, ent_columns
        # ),
    }

    content = convert(
        repr=drepr,
        resources=resources,
        format=format,
        progfile=os.environ.get("DREPR_GEN_FILE"),
    )
    assert isinstance(content, str)
    return content


def convert_data_from_sm(
    table: ColumnBasedTable,
    sm: SemanticModel,
    ontology: IdentObj[Ontology],
    ident_props: Optional[set[str]] = None,
    format: OutputFormat = OutputFormat.TTL,
    datatype_norms: Optional[dict[str, Callable]] = None,
    base_uri: str = "",
) -> str:
    drepr = create_drepr_model(
        table, sm, ontology, ident_props, datatype_norms, base_uri
    )
    return convert_data_from_drepr(
        table=table,
        drepr=drepr,
        format=format,
    )
