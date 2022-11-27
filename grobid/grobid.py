import glob
import logging
import os.path

from grobid_client.grobid_client import GrobidClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_pdf(directory):

    files = glob.glob(f"{directory}/*.pdf")
    filename = "".join(files[0].split("/")[-1].split(".")[:-1])
    logger.info(f"article PDF filename root: {filename}")

    tei_xml_filepath = f"{directory}/{filename}.tei.xml"

    if os.path.exists(tei_xml_filepath):
        logging.info("TEI already generated, using")
        return tei_xml_filepath

    client = GrobidClient(config_path="grobid/grobid_config.json")

    res = client.process(
        "processFulltextDocument",
        directory,
        include_raw_citations=True,
        include_raw_affiliations=True,
        segment_sentences=True,
        generateIDs=True,
        n=4,
    )

    print("PDF parsed via GROBID")
    return tei_xml_filepath
