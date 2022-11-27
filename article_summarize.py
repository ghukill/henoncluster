from gpt3.gpt3 import tldr
from grobid.grobid import parse_pdf
from tei.tei import delb_parse


def run_test(directory):

    # parse pdf
    tei_filepath = parse_pdf(directory)

    tei = delb_parse(tei_filepath)

    body_divs = tei.css_select("text body div")

    for bd in body_divs:
        heads = bd.css_select("head")
        if len(heads) != 1:
            continue
        head = heads[0]
        print("##################################################################")
        print(head.attributes["n"], head.full_text)
        print("##################################################################\n")
        summary = tldr(bd.full_text, max_tokens=256)
        print(summary, "\n\n")
