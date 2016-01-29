#!/usr/bin/python

#from HTMLParser import HTMLParser
import requests
from lxml import html
import jinja2
import boto
import os
import hashlib

URL = 'https://launchpad.net/ubuntu/trusty/+source/openssl/+changelog'

data = {}
packages = requests.get(URL)
tree = html.fromstring(packages.text)

data['author'] = tree.xpath("//*[@id='watermark-heading']/a[last()]/text()")
data['title'] = tree.xpath("//*[@id='maincontent']//h1//text()")[0].strip()

data['items'] = []
for row in tree.xpath("//pre[@class='changelog']"):
  rowlines = row.text_content().splitlines()
  rowstrs = [x.strip() for x in rowlines if x.strip()]
  data['items'].append( {
    'title': rowlines[0],
    'link': URL,
    'content': "<pre>" + "\n".join( (rowstrs) ) + "</pre>",
    'id': hashlib.sha256(rowlines[0]).hexdigest()
  })


# idea stolen from codeape on stackoverflow: http://stackoverflow.com/a/2101186/659298
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_atom = jinja2.Environment(loader=jinja2.FileSystemLoader(curr_dir)).get_template("atomtemplate.xml.j2").render(data)

s3 = boto.connect_s3()
s3key = s3.get_bucket('tedder').new_key('rss/ppa/trusty-openssl.atom')
s3key.set_metadata('Content-Type', 'application/atom+xml')
s3key.set_contents_from_string(output_atom, replace=True, reduced_redundancy=True, headers={'Cache-Control':'public, max-age=3600'}, policy="public-read")


#p = HTMLParser()
#p.feed(packages.text)


