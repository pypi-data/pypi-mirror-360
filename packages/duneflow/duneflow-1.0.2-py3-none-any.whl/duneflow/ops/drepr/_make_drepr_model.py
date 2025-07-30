from __future__ import annotations

import inspect
import re
import textwrap
from copy import deepcopy
from functools import lru_cache, partial
from pathlib import Path as PathlibPath
from typing import Callable, Mapping, Optional

import drepr.models.sm as drepr_sm
import duneflow.ops.drepr._transformations as _transformations
from drepr.models.prelude import (
    DREPR_URI,
    AlignedStep,
    Alignment,
    Attr,
    CSVProp,
    DRepr,
    IndexExpr,
    Path,
    PMap,
    POutput,
    Preprocessing,
    PreprocessingType,
    RangeAlignment,
    RangeExpr,
    Resource,
    ResourceType,
)
from kgdata.models import Ontology
from libactor.cache import IdentObj
from rdflib import XSD
from slugify import slugify
from sm.inputs.table import ColumnBasedTable
from sm.outputs.semantic_model import (
    ClassNode,
    DataNode,
    Edge,
    LiteralNode,
    LiteralNodeDataType,
    SemanticModel,
)


def create_drepr_model(
    table: ColumnBasedTable,
    sm: SemanticModel,
    ontology: IdentObj[Ontology],
    ident_props: Optional[set[str]] = None,
    datatype_norms: Optional[dict[str, Callable]] = None,
    base_uri: str = "",
) -> DRepr:
    """Create a DRepr model from a table and semantic model.

    Args:
        table: The column-based table
        sm: The semantic model
        ontology: The ontology
        ident_props: List of properties that identify entity columns (e.g., rdfs:label)
        datatype_norms: Mapping from datatype to transformation code
        base_uri: Base URI for the new entities created based on the model (DREPR_URI)
    Returns:
        A DRepr model
    """
    if ident_props is None:
        ident_props = set()
    if datatype_norms is None:
        datatype_norms = {
            "http://www.opengis.net/ont/geosparql#wktLiteral": _transformations.global_coordinate,
            str(XSD.int): _transformations.integer_number,
            str(XSD.decimal): _transformations.decimal_number,
            str(DREPR_URI): _transformations.drepr_uri,
        }

    nrows, ncols = table.shape()
    existing_attr_names = {}
    get_attr_id = partial(
        _get_attr_id, table=table, existing_attr_names=existing_attr_names
    )

    get_ent_attr_id = lambda ci: f"{get_attr_id(ci)}__ent"
    ent_dnodes = get_entity_data_nodes(sm, ident_props)

    attrs: list[Attr] = []
    for col in table.columns:
        attr = Attr(
            id=get_attr_id(col.index),
            resource_id="table",
            path=Path(
                steps=[
                    RangeExpr(start=1, end=nrows + 1, step=1),
                    IndexExpr(val=col.index),
                ]
            ),
            missing_values=[""],
        )
        if (
            len(col.values) > 0
            and not isinstance(col.values[0], str)
            and isinstance(col.values[0], list)
        ):
            # TODO: this is a list, if the datatype is not a list, then we are going to iterate into items of the list
            # how do we know that this datatype is a list? - for now, we just assume that the datatype is not a list
            attr.path.steps.append(RangeExpr(start=0, end=None, step=1))

        attrs.append(attr)

    # generate new attributes for the entity columns
    # attrs += [
    #     Attr(
    #         id=get_ent_attr_id(node.col_index),
    #         resource_id="entity",
    #         path=Path(
    #             steps=[
    #                 RangeExpr(start=1, end=nrows + 1, step=1),
    #                 IndexExpr(val=node.col_index),
    #             ]
    #         ),
    #         missing_values=[""],
    #     )
    #     for node in ent_dnodes
    # ]

    dsm = _get_drepr_sm(
        sm=sm,
        ontology=ontology.value,
        ident_props=ident_props,
        get_attr_id=get_attr_id,
        get_ent_attr_id=get_ent_attr_id,
    )

    aligns: list[Alignment] = []
    for ci in range(1, len(table.columns)):
        aligns.append(
            RangeAlignment(
                source=get_attr_id(table.columns[0].index),
                target=get_attr_id(table.columns[ci].index),
                aligned_steps=[AlignedStep(source_idx=0, target_idx=0)],
            )
        )
    for node in ent_dnodes:
        aligns.append(
            RangeAlignment(
                source=get_attr_id(table.columns[0].index),
                target=get_ent_attr_id(node.col_index),
                aligned_steps=[AlignedStep(source_idx=0, target_idx=0)],
            )
        )

    datatype_transformations: list[Preprocessing] = []
    for node in sm.nodes():
        if not isinstance(node, DataNode):
            continue

        old_attr_id = get_attr_id(node.col_index)
        (old_attr,) = [attr for attr in attrs if attr.id == old_attr_id]

        inedges = sm.in_edges(node.id)
        new_trans: list[tuple[Edge, Optional[Preprocessing]]] = []
        for inedge in inedges:
            datatype = ontology.value.props[
                ontology.value.kgns.uri_to_id(inedge.abs_uri)
            ].datatype

            if datatype in datatype_norms:
                norm_func = _get_python_code(datatype_norms[datatype], base_uri)
                new_trans.append(
                    (
                        inedge,
                        Preprocessing(
                            type=PreprocessingType.pmap,
                            value=PMap(
                                resource_id="table",
                                path=deepcopy(old_attr.path),
                                code=norm_func,
                                change_structure=False,
                            ),
                        ),
                    )
                )
            else:
                new_trans.append((inedge, None))

        if len(inedges) > 1 and any(x[1] is not None for x in new_trans):
            # this column is used for multiple relationships, but some relationships required
            # transforming the data, so we need to create a new attribute for those transformations
            # to avoid overwriting the original attribute
            for idx, (inedge, transformation) in enumerate(new_trans):
                if transformation is None:
                    continue

                new_attr_id = old_attr_id + f"_{idx}"
                transformation.set_output(
                    POutput(resource_id=None, attr=new_attr_id, attr_path=None)
                )
                # we need to map previous attribute id to the new attribute id
                uid = str(inedge.source)
                vid = str(inedge.target)

                # so we need to remove the old edge and add a new edge
                (match_edge,) = [
                    edge
                    for edge in dsm.get_edges_between_nodes(uid, vid)
                    if edge.label == inedge.rel_uri
                ]
                new_vid_id = vid + f"_{idx}"
                dsm.nodes[new_vid_id] = drepr_sm.DataNode(
                    new_vid_id, attr_id=new_attr_id
                )
                dsm.edges[match_edge.edge_id] = drepr_sm.Edge(
                    edge_id=match_edge.edge_id,
                    source_id=uid,
                    target_id=new_vid_id,
                    label=inedge.rel_uri,
                )
                # add alignment to the new attribute id
                aligns.append(
                    RangeAlignment(
                        source=old_attr_id,
                        target=new_attr_id,
                        aligned_steps=[
                            AlignedStep(source_idx=i, target_idx=i)
                            for i, step in enumerate(old_attr.path.steps)
                            if isinstance(step, RangeExpr)
                        ],
                    )
                )
        datatype_transformations.extend(x[1] for x in new_trans if x[1] is not None)

    return DRepr(
        resources=[
            Resource(id="table", type=ResourceType.JSON),
            # Resource(id="entity", type=ResourceType.CSV, prop=CSVProp()),
        ],
        preprocessing=datatype_transformations,
        attrs=attrs,
        aligns=aligns,
        sm=dsm,
    )


def _get_attr_id(ci: int, table: ColumnBasedTable, existing_attr_names: dict):
    """Get the attribute ID for a column index to use in a D-Repr model."""
    cname = slugify(table.get_column_by_index(ci).clean_name or "").replace("-", "_")
    if cname == "":
        return "col_" + str(ci)
    if cname[0].isdigit():
        cname = "_" + cname

    m = re.match(r"\d+([^\d].*)", cname)
    if m is not None:
        cname = m.group(1)
    if existing_attr_names.get(cname, None) != ci:
        return cname + "_" + str(ci)

    existing_attr_names[cname] = ci
    return cname


def _get_drepr_sm(
    sm: SemanticModel,
    ontology: Ontology,
    ident_props: set[str],
    get_attr_id: Callable[[int], str],
    get_ent_attr_id: Callable[[int], str],
) -> drepr_sm.SemanticModel:
    """Convert sm model into drepr model.

    Args:
        sm: the semantic model we want to convert
        kgns: the knowledge graph namespace
        kgns_prefixes: the prefixes of the knowledge graph namespace
        ontprop_ar: mapping from the id to ontology property
        ident_props: list of properties that telling a data node contains entities (e.g., rdfs:label)
        get_attr_id: get attribute id from column index
        get_ent_attr_id: for each entity column, to generate url, we create an extra attribute containing the entity uri, this function get its id based on the column index
    """
    nodes = {}
    edges = {}

    for node in sm.nodes():
        if isinstance(node, ClassNode):
            nodes[str(node.id)] = drepr_sm.ClassNode(
                node_id=str(node.id), label=node.rel_uri
            )
        elif isinstance(node, DataNode):
            # find data type of this node, when they have multiple data types
            # that do not agree with each other, we don't set the datatype
            # usually, that will be displayed from the UI so users know that
            datatypes = set()
            for inedge in sm.in_edges(node.id):
                datatype = ontology.props[
                    ontology.kgns.uri_to_id(inedge.abs_uri)
                ].datatype
                if datatype == "":
                    continue
                datatype = drepr_sm.DataType(datatype, ontology.kgns.prefix2ns)
                datatypes.add(datatype)

            nodes[str(node.id)] = drepr_sm.DataNode(
                node_id=str(node.id),
                attr_id=get_attr_id(node.col_index),
                data_type=next(iter(datatypes)) if len(datatypes) == 1 else None,
            )
        elif isinstance(node, LiteralNode):
            if node.datatype == LiteralNodeDataType.Entity:
                datatype = drepr_sm.PredefinedDataType.drepr_uri.value
            else:
                assert node.datatype == LiteralNodeDataType.String
                datatype = drepr_sm.PredefinedDataType.xsd_string.value

            nodes[str(node.id)] = drepr_sm.LiteralNode(
                node_id=str(node.id), value=node.value, data_type=datatype
            )

    used_ids = {x for edge in sm.edges() for x in [str(edge.source), str(edge.target)]}
    for node_id in set(nodes.keys()).difference(used_ids):
        del nodes[node_id]

    for edge in sm.edges():
        edges[len(edges)] = drepr_sm.Edge(
            edge_id=len(edges),
            source_id=str(edge.source),
            target_id=str(edge.target),
            label=edge.rel_uri,
        )

    # print(edges)

    # add drepr:uri relationship
    for node in get_entity_data_nodes(sm, ident_props):
        new_node_id = str(node.id) + ":ents"
        nodes[new_node_id] = drepr_sm.DataNode(
            node_id=new_node_id,
            attr_id=get_ent_attr_id(node.col_index),
            data_type=drepr_sm.PredefinedDataType.drepr_uri.value,
        )
        inedges = [
            inedge for inedge in sm.in_edges(node.id) if inedge.abs_uri in ident_props
        ]
        assert len(inedges) == 1
        inedge = inedges[0]
        edges[len(edges)] = drepr_sm.Edge(
            edge_id=len(edges),
            source_id=str(inedge.source),
            target_id=new_node_id,
            # special predicate telling drepr to use as uri of entity, instead of generating a blank node
            label=ontology.kgns.get_rel_uri(DREPR_URI),
        )

    prefixes = ontology.kgns.prefix2ns.copy()
    prefixes.update(drepr_sm.SemanticModel.get_default_prefixes())
    return drepr_sm.SemanticModel(
        nodes=nodes,
        edges=edges,
        prefixes=prefixes,
    )


@lru_cache()
def _get_python_code(func: Callable, base_uri: str = "") -> str:
    func_code = inspect.getsource(func)
    body = textwrap.dedent("\n".join(func_code.splitlines()[1:]))
    body = body.replace(r"{{ BASE_URI }}", base_uri)
    return body


def get_entity_data_nodes(sm: SemanticModel, ident_props: set[str]) -> list[DataNode]:
    """Get data nodes that represent entities in the semantic model."""
    ent_dnodes = []
    for node in sm.iter_nodes():
        if not isinstance(node, DataNode):
            continue

        for inedge in sm.in_edges(sm.get_data_node(node.col_index).id):
            if inedge.abs_uri in ident_props:
                ent_dnodes.append(node)

    return ent_dnodes
