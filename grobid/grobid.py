
from grobid_client.grobid_client import GrobidClient

client = GrobidClient(config_path="grobid/grobid_config.json")

res = client.process(
    "processFulltextDocument",
    "documents",
    include_raw_citations=True,
    include_raw_affiliations=True,
    segment_sentences=True,
    n=4
)