# TEI

https://github.com/delb-xml/delb-py

## Parse TEI XML

```python
from tei.tei import delb_parse

tei = delb_parse('tmp/foo.xml')
```

## Examples

`TEI.text.body` nodes
```python

# find body div nodes
body_divs = tei.css_select('text body div')

# get first
d0 = tei.css_select('text body div')[0]

# get head
d0_head = d0.css_select('head')[0]
"""
In [195]: d0_head.full_text
Out[195]: 'Introduction'
"""
```

