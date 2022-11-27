"""
HenonCluster flask app
"""

import json
import logging

from flask import Flask, render_template

from gpt3.gpt3 import tldr
from grobid.grobid import parse_pdf
from tei.tei import delb_parse, prepare_graph_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>HenonCluster</p>"


@app.route("/article/summarize")
def article_summarize():

    """ """

    # DEBUG: hardcoded input
    DIRECTORY = "tmp/test1"
    SUMMARIZE = False

    # parse pdf
    tei_filepath = parse_pdf(DIRECTORY)

    # parse TEI XML with delb
    tei = delb_parse(tei_filepath)

    # NOTE: move this to tei module ---------------------------------------------------------------
    # summarize sections
    summaries = {}
    text_sections = tei.xpath("//text/body/div")
    for ts in text_sections:

        # extract head information
        try:
            ts_head = ts.xpath("head")[0]
            ts_head_id = ts_head.attributes["{http://www.w3.org/XML/1998/namespace}id"]
            ts_head_n = ts_head.attributes["n"]
            section_name = f"{ts_head_n}, '{ts_head.full_text}'"
        except:
            continue

        # summarize text section
        if SUMMARIZE:
            logging.info(f"summarizing section: {section_name}")
            summary = tldr(ts.full_text, max_tokens=256)
        else:
            summary = "Not summarizing..."

        # add to summaries
        summaries[str(ts_head_id)] = dict(
            section_name=section_name,
            summary=summary,
        )
    # NOTE: move this to tei module ---------------------------------------------------------------

    # prepare tei graph data
    graph_data = prepare_graph_data(tei, text_sections, summaries)

    return render_template(
        "article_summarize.html",
        article=dict(
            title=tei.xpath("//teiHeader/fileDesc/titleStmt/title")[0].full_text
        ),
        summaries=json.dumps(summaries, indent=4),
        elements=json.dumps(graph_data, indent=4),
    )
