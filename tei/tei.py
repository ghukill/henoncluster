import delb


def delb_parse(path):

    print("TEI XML parsed via delb")
    return delb.Document(delb.Path(path))
