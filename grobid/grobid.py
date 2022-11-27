import glob

from grobid_client.grobid_client import GrobidClient


def parse_pdf(directory):

    files = glob.glob(f"{directory}/*.pdf")
    filename = "".join(files[0].split("/")[-1].split(".")[:-1])
    print(filename)

    client = GrobidClient(config_path="grobid/grobid_config.json")

    res = client.process(
        "processFulltextDocument",
        directory,
        include_raw_citations=True,
        include_raw_affiliations=True,
        segment_sentences=True,
        n=4,
    )

    print("PDF parsed via GROBID")
    return f"{directory}/{filename}.tei.xml"
