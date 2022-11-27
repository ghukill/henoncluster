import logging

import delb

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delb_parse(path):

    logging.info("TEI XML parsed via delb")
    return delb.Document(delb.Path(path))


def prepare_graph_data(tei, text_sections, summaries: dict):

    logging.info("preparing TEI graph")

    nodes = []  # e.g. {"data": {"id": "a"}}
    edges = []  # e.g. {"data": {"id": "ab", "source": "a", "target": "b"}}

    # loop through sections and add nodes and edges
    for ts_id, ts in summaries.items():
        nodes.append({"data": {"id": ts_id, "name": ts["section_name"]}})

    # add references
    refs = tei.xpath("//text/back/div[@type='references']/listBibl//biblStruct")
    for ref in refs:

        # get ref id and name
        ref_id = str(ref.attributes["{http://www.w3.org/XML/1998/namespace}id"])
        ref_raw = ref.xpath("*[@type='raw_reference']")[0].full_text

        # add node
        nodes.append({"data": {"id": ref_id, "name": ref_id}})

        # look for citations, e.g. <ref type="bibr" target="#b0">
        citations = tei.xpath(f"//ref[@target='#{ref_id}']")

        # loop through citations and navigate back to text section
        for citation in citations:
            for ancestor in citation.ancestors():
                if ancestor.qualified_name == "{http://www.tei-c.org/ns/1.0}div":
                    ts_head_id = str(
                        ancestor.xpath("head")[0].attributes[
                            "{http://www.w3.org/XML/1998/namespace}id"
                        ]
                    )
                    edges.append(
                        {
                            "data": {
                                "id": f"{ref_id}_{ts_head_id}",
                                "source": ref_id,
                                "target": ts_head_id,
                            }
                        }
                    )

                    # add back to summaries
                    summaries[ts_head_id]["citations"].add((ref_id, ref_raw))

    return summaries, nodes + edges
