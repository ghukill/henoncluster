# GROBID

  * https://hub.docker.com/r/grobid/grobid
  * https://komax.github.io/blog/text/mining/grobid/
  * https://github.com/kermitt2/grobid_client_python

## Installation

### Server
https://komax.github.io/blog/text/mining/grobid/

```shell
wget https://github.com/kermitt2/grobid/archive/0.7.2.zip && unzip 0.7.2.zip
./gradlew clean install
./gradlew run
```

### Python client

```shell
git clone https://github.com/kermitt2/grobid_client_python
cd grobid_client_python
python3 setup.py install
```

## Parsing TEI XML

https://komax.github.io/blog/text/python/xml/parsing_tei_xml_python/

```python
# get DOI
soup.find('idno', type='DOI').getText()
```

