"""
HenonCluster flask app
"""

from collections import defaultdict
import glob
import json
import logging
import os
import pickle
import time

from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import fuzz
from natsort import natsorted
from nltk import ngrams
import pdfplumber

from gpt3.gpt3 import summarize_text
from grobid.grobid import parse_pdf
from tei.tei import delb_parse, prepare_graph_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False


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

    DIRECTORY = request.args.get("directory")
    TARGET = request.args.get("target")
    NGRAM_SIZE = int(request.args.get("ngram_size", 8))
    PAGE_LIMIT = int(request.args.get("page_limit", 1000))
    logging.info("%s %s %s %s" % (DIRECTORY, TARGET, NGRAM_SIZE, PAGE_LIMIT))

    pdfs = {}

    for filepath in glob.glob(f"{DIRECTORY}/*.pdf"):

        # extract filename
        pdf_filename = filepath.split("/")[-1]
        cache_filepath = f"{DIRECTORY}/{pdf_filename}.{PAGE_LIMIT}.bow"
        logging.info(f"extracting text: {pdf_filename}")

        # extract text
        if os.path.exists(cache_filepath):
            logging.info(f"CACHE HIT: {cache_filepath}")
            with open(cache_filepath, "rb") as f:
                bow = pickle.load(f)
        else:
            with pdfplumber.open(filepath) as pdf:
                bow = []
                for page in pdf.pages:
                    if page.page_number > PAGE_LIMIT:
                        continue
                    text = page.extract_text().replace("\n", " ").lower()
                    bow.extend(text.split(" "))

                # cleanup BOW
                # TODO: improve non-word removal
                exclude = [" ", ""]
                bow = [w for w in bow if w not in exclude]

                with open(cache_filepath, "wb") as f:
                    pickle.dump(bow, f)

        # add to pdfs
        pdfs[pdf_filename] = list(dict.fromkeys(list(ngrams(bow, NGRAM_SIZE))))

    # loop through and compare
    collisions = defaultdict(list)
    target_ngs = pdfs[TARGET]
    for pdf, ngs in pdfs.items():
        possible = []
        if pdf == TARGET:
            continue
        for target_ng in target_ngs:
            for ng in ngs:
                if target_ng == ng:
                    possible.append(" ".join(target_ng))
        print(possible)
        if len(possible) == 0:
            continue
        elif len(possible) == 1:
            collisions[pdf] = possible
        else:
            collisions[pdf].append(possible[0])
            for i in range(1, (len(possible) - 1)):
                p = fuzz.partial_ratio(possible[i], possible[i + 1])
                print(p)
                if p < 80:
                    collisions[pdf].append(possible[i])

        logging.info(f"found {len(collisions[pdf])} collisions against {pdf}")

    return jsonify(collisions)
