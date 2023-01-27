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
import numpy as np
import pandas as pd
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
    NGLOW = int(request.args.get("nglow", 8))
    NGHIGH = int(request.args.get("nghigh", 50))
    PAGE_LIMIT = int(request.args.get("page_limit", 1000))
    logging.info("%s %s %s %s %s" % (DIRECTORY, TARGET, NGLOW, NGHIGH, PAGE_LIMIT))

    pdfs = {}

    # TODO: abstract to BOW helper
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

        pdfs[pdf_filename] = bow

    # generate dataframes
    dfs = []
    for pdf, bow in pdfs.items():
        data = []
        for ng_size in range(NGLOW, NGHIGH):
            _ngs = list(ngrams(bow, ng_size))
            data.extend(
                list(
                    zip(
                        np.array([pdf] * len(_ngs)),
                        np.array([ng_size] * len(_ngs)),
                        _ngs,
                    )
                )
            )
        dfs.append(pd.DataFrame(data, columns=["pdf", "ngram_size", "ngram"]))
    df = pd.concat(dfs)

    # create phrase from ngram
    df.ngram = df.ngram.apply(lambda x: " ".join(x))

    # drop true duplicates
    df = df.drop_duplicates(keep="first")

    # get phrase collisions
    colls = df[df.ngram.duplicated(keep=False)]

    # filter only rows where ngram is collision with target PDF
    colls = colls[
        colls.ngram.isin(colls[colls.pdf == TARGET].ngram) & ~(colls.pdf == TARGET)
    ]

    # sort and remove ngrams that are embedded in a larger one
    colls = colls.sort_values(by="ngram_size")

    def remove_sub_gram(ngs, ng):
        for _ng in ngs:
            if ng in _ng and ng != _ng:
                return True
        return False

    colls["sub_ngram"] = colls.ngram.apply(lambda ng: remove_sub_gram(colls.ngram, ng))

    # return only the longest
    unq_df = colls[~colls.sub_ngram]

    # reverse sort
    unq_df = unq_df.sort_values(by=["pdf", "ngram_size"], ascending=False)

    # return as HTML
    return unq_df.to_html()
