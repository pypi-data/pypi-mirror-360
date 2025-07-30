
![PyPI version](https://img.shields.io/pypi/v/markpub_bskypost)  
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/markpub_bskypost)](https://pypi.org/project/markpub_bskypost/)

Bluesky Comment support for MarkPub and MassiveWiki websites
=========================

Python package to  
(1) post a MarkPub or MassiveWiki webpage link to Bluesky, and  
(2) display any comments and likes made to that Bluesky post on the referenced website page.  

Tested with Python 3.12.

This code is an excerpt of the code described in the blog post ["Posting via the Bluesky API"](https://atproto.com/blog/create-post).

Gratitude to [Emily Liu](https://emilyliu.me/) and [Cory Zue](https://www.coryzue.com/)  

-----

**To install**:

``` shell
pip install markpub_bskypost
```  

Note: this package will be transferred from this test index to `pypi.org` .  

**For a list of options and arguments**:

```shell
markpub_bskypost -h
```   

**Some configuration notes and suggestions**  

Bluesky and GitHub credentials are needed to post to Bluesky and to update pages in a GitHub repository. These can be provided as arguments on the command line, or as local shell environment variables.  

Environment Variables:  

Create a `.env` file in your project root with the following variables:

```
ATP_PDS_HOST=your_bluesky_host_here
ATP_AUTH_HANDLE=your_bluesky_handle_here
ATP_AUTH_PASSWORD=your_bluesky_password_here
GH_TOKEN=your_GitHub_token_here
```

If ATP_PDS_HOST is not specified “https://bsky.social” is the default.  

**N.B.**: Never commit your `.env` file to version control. Add it to your `.gitignore` file.

Website host and Git repository:  

The host on which the website is deployed, and the repository holding the Markdown files can be specified on the command line, or in a file in the working directory named `bskypost.yaml` . Here is an example file:  

```yaml
deploy_site: socialpraxis.netlify.app
repo_name: band/technosocial-praxis
```  

**Use example**:  

This program is run in a terminal application and from the `.markpub` directory of your repository.  

Running `markpub_bskypost` yields  

``` shell
Enter the Markdown file name: 
```   
One can enter a full-path, or a relative path, to a Markdown file in the repository, or an Obsidian URL (copied from the Obsidian file browser;  
for example:
`obsidian://open?vault=technosocial-praxis&file=notas%2F20250325-testnote` )  

`markpub_bksypost` generates the webpage URL to embed in the post
and then prompts for the content of the Bluesky post (showing how many
characters are available for the post text).  
```shell
Enter bluesky post text (238 characters available): 
```  

