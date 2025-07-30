from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha512
from pathlib import Path
from typing import Optional

from deprecated import deprecated
from kgdata.models import Ontology
from libactor.actor import Actor
from libactor.cache import IdentObj
from sm.inputs.prelude import ColumnBasedTable
from sm.namespaces.prelude import KnowledgeGraphNamespace
from sm.outputs import SemanticModel, deser_simple_tree_yaml, ser_simple_tree_yaml


@dataclass
class SemanticModelCuratorArgs:
    workdir: Path
    format: str


@deprecated(reason="use duneflow.ops.curation.semantic_model_curator instead")
class SemanticModelCuratorActor(Actor[SemanticModelCuratorArgs]):

    def forward(
        self,
        table: ColumnBasedTable,
        sm: Optional[IdentObj[SemanticModel]],
        kgns: KnowledgeGraphNamespace,
    ) -> IdentObj[SemanticModel]:
        self.params.workdir.mkdir(parents=True, exist_ok=True)

        sm_file = self.params.workdir / f"description.{self.params.format}"
        if not sm_file.exists():
            assert sm is not None, sm_file
            if sm.value.num_edges() > 0:
                ser_simple_tree_yaml(table, sm.value, kgns, sm_file)
            return sm
        else:
            return IdentObj(
                key=sha512(sm_file.read_bytes()).hexdigest(),
                value=deser_simple_tree_yaml(table, sm_file),
            )


def semantic_model_curator(
    table: ColumnBasedTable,
    sm: Optional[IdentObj[SemanticModel]],
    kgns: KnowledgeGraphNamespace,
    outdir: Path,
    format: str,
    filename: str = "description",
) -> IdentObj[SemanticModel]:
    sm_file = outdir / f"{filename}.{format}"
    if not sm_file.exists():
        assert sm is not None, sm_file
        if sm.value.num_edges() > 0:
            ser_simple_tree_yaml(table, sm.value, kgns, sm_file)
        return sm
    else:
        return IdentObj(
            key=sha512(sm_file.read_bytes()).hexdigest(),
            value=deser_simple_tree_yaml(table, sm_file),
        )
