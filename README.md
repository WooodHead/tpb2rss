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
tpb2rss.xml_from_url(A, B, C, D)
```

- `A` (required): search term or URL (*string*)

- `B` (optional, `True` by default): ignores any info on pagination and ordination from the given URL, forcing it to return the most recent items by upload date (*boolean*)

- `C` (optional, `https://thepiratebay.se` by default): set a mirror to use (*string*)

- `D` (optional, `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36` by default): set an User Agent when downloading the page (*string*)

Creating a XML from a TPB saved page:
```
tpb2rss.xml_from_file(FILENAME)
```

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
