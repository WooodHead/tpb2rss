TPB2RSS
=======

A python script to generate a RSS feed from a The Pirate Bay search

Usage
-----

```
./tpb2rss.py ( TPB_URL | SEARCH_TERM ) [ OUTPUT_FILE ]
```

Calling from another python program
-----------------------------------

Import the script:

```
from tpb2rss import ThePirateFeed
```

Creating a XML from a TPB url:

```
ThePirateFeed(input_string, force_most_recent, tpburl, agent)
```

- `input_string` (required): search term or URL (*string*)

- `force_most_recent` (optional, `True` by default): ignores any info on pagination and ordination from the given URL, forcing it to return the most recent items by upload date (*boolean*)

- `tpburl` (optional, `https://thepiratebay.se` by default): set a mirror to use (*string*)

- `agent` (optional, `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36` by default): set an User Agent when downloading the page (*string*)

Installing on OpenShift
-----------------------

Read my installation guide [here](http://brunelli.me/thinny/blog/tpb2rss-openshift)

Dependencies
------------

[Python >= 3.3](http://docs.python.org/3/)

License
-------

[Apache License 2.0](https://github.com/camporez/tpb2rss/raw/master/LICENSE)
