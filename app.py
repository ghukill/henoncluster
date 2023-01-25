"""
HenonCluster flask app
"""

from collections import defaultdict
import glob
import json
import logging
import time

from flask import Flask, render_template, request
from natsort import natsorted
from nltk import ngrams
import pdfplumber

from gpt3.gpt3 import summarize_text
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

    t0 = time.time()

    # DEBUG: hardcoded input
    DIRECTORY = "tmp/test1"
    SUMMARIZE = True

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
            summary = summarize_text(ts.full_text, max_tokens=256)
        else:
            summary = "Not summarizing..."

        # add to summaries
        summaries[str(ts_head_id)] = dict(
            section_name=section_name, summary=summary, citations=set()
        )
    # NOTE: move this to tei module ---------------------------------------------------------------

    # prepare tei graph data
    summaries, graph_data = prepare_graph_data(tei, text_sections, summaries)

    # prepare for output
    for k, v in summaries.items():
        v["citations"] = natsorted(list(v["citations"]))

    logging.info(f"total article summarization: {time.time()-t0}")

    return render_template(
        "article_summarize.html",
        article=dict(
            title=tei.xpath("//teiHeader/fileDesc/titleStmt/title")[0].full_text
        ),
        summaries=json.dumps(summaries, indent=4),
        elements=json.dumps(graph_data, indent=4),
    )


@app.route("/articles/compare")
def articles_compare():

    NGRAM_SIZE = 8
    PAGE_LIMIT = 2

    # DIRECTORY = "tmp/test1"
    DIRECTORY = request.args.get("directory")
    TARGET = request.args.get("target")
    logging.info(f"working on directory: {DIRECTORY}, target: {TARGET}")

    pdfs = {}
    for filepath in glob.glob(f"{DIRECTORY}/*.pdf"):

        # extract filename
        pdf_filename = filepath.split("/")[-1]
        logging.info(f"working on PDF: {pdf_filename}")

        # extract text
        with pdfplumber.open(filepath) as pdf:
            bow = []
            for page in pdf.pages:
                if page.page_number >= PAGE_LIMIT:
                    continue
                text = page.extract_text().replace("\n", " ").lower()
                bow.extend(text.split(" "))
                logging.info(f"page {page.page_number} completed")

            # cleanup
            # TODO: improve non-word removal
            exclude = [" ", ""]
            bow = [w for w in bow if w not in exclude]

        # add to pdfs
        pdfs[pdf_filename] = list(ngrams(bow, NGRAM_SIZE))

        # loop through and compare
        collisions = defaultdict(list)
        target_ngs = pdfs[TARGET]
        for pdf, ngs in pdfs.items():
            if pdf == TARGET:
                continue
            logging.info(f"checking against: {pdf}")
            for target_ng in target_ngs:
                for ng in ngs:
                    if target_ng == ng:
                        collisions[pdf].append(target_ng)

    return collisions
