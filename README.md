TPB2RSS
=======

A python script to generate a RSS feed from a thepiratebay.se search

Usage
-----

```
./tpb2rss.py ( INPUT_FILE | TPB_URL | SEARCH_TERM ) [ OUTPUT_FILE ]
```

Calling from another python program
-----------------------------------

Import the program:

```
import tpb2rss
```

Creating a XML from a TPB url:

```
tpb2rss.xml_from_url(A, B, C)
```

Creating a XML from a TPB saved page:
```
tpb2rss.xml_from_file(A, B, C)
```

- `A` (required): search term, URL or filename

- `B` (optional, `false` by default): preserve pagination and order info from the URL (`true` or `false`)

- `C` (optional, `https://thepiratebay.se` by default): set a mirror to use (*string*)

Installing on OpenShift
-----------------------

Read my installation guide [here](http://camporez.com/blog/tpb2rss-openshift)

Dependencies
------------

- [Python 2](http://docs.python.org/2/)
- [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
- [urllib2](https://docs.python.org/2/library/urllib2.html) library (default in Python 2.x)
- [datetime](https://docs.python.org/2/library/datetime.html) library (default in Python 2.x)

License
-------

[Apache License 2.0](https://github.com/camporez/tpb2rss/raw/master/LICENSE)
