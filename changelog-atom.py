#!/usr/bin/env python3

#from HTMLParser import HTMLParser
import requests
from lxml import html
import jinja2
import boto3
import os
import hashlib
import six

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
    'id': hashlib.sha256(six.b(rowlines[0])).hexdigest()
  })


# idea stolen from codeape on stackoverflow: http://stackoverflow.com/a/2101186/659298
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_atom = six.BytesIO(jinja2.Environment(loader=jinja2.FileSystemLoader(curr_dir)).get_template("atomtemplate.xml.j2").render(data).encode('utf-8'))

s3 = boto3.client('s3')
s3.upload_fileobj(output_atom, 'dyn.tedder.me', 'rss/ppa/trusty-openssl.atom', ExtraArgs={
  'CacheControl': 'public, max-age=3600',
  'ContentType': 'application/atom+xml',
  'ACL': 'public-read',
  'StorageClass': 'REDUCED_REDUNDANCY'
})

#p = HTMLParser()
#p.feed(packages.text)


