
Microblogging support for MarkPub and MassiveWiki websites
=========================

Script to (1) post a link to a MarkPub or MassiveWiki website to Bluesky,
and (2) display any comments and likes made to that Bluesky post on
the referenced website page.  

To run this Python script, 'requests' and 'bs4' (BeautifulSoup) packages must be installed. Tested with Python 3.12.

This code is an excerpt of the code described in the blog post ["Posting via the Bluesky API"](https://atproto.com/blog/create-post).

Gratitude to [Emily Liu](https://emilyliu.me/) and [Cory Zue](https://www.coryzue.com/)  

-----

To install:

``` shell
pip install --extra-index-url https://test.pypi.org/simple/ markpub_bskypost
```  


For a list of options and arguments:

```shell
markpub_bskypost
```   


