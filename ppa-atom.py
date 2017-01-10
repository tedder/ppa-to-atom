#!/usr/bin/env python3

#from HTMLParser import HTMLParser
import requests
from lxml import html
import jinja2
import boto3
import six
import os
import hashlib

URL = 'https://launchpad.net/~rquillo/+archive/ansible/+packages'

data = {}
packages = requests.get(URL)
tree = html.fromstring(packages.text)

data['author']= tree.xpath("//*[@itemprop='breadcrumb']/li[1]/a/text()")[0]
data['title'] = ' : '.join([x.strip() for x in tree.xpath("//*[@itemprop='breadcrumb']/li//text()") if x.strip()])

data['items'] = []
for row in tree.xpath("//*[@id='packages_list']/*//tr[contains(@class,'archive_package_row')]"):
  rowstrs = [x.strip() for x in row.xpath("td//text()") if x.strip()]
  if not rowstrs:
    continue
  content = ' '.join((rowstrs)).encode('utf-8')
  data['items'].append( {
    'title': rowstrs[0][0],
    'link': URL,
    'content': content,
    'id': hashlib.sha256(content).hexdigest()
  })

# idea stolen from codeape on stackoverflow: http://stackoverflow.com/a/2101186/659298
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_atom = six.BytesIO(jinja2.Environment(loader=jinja2.FileSystemLoader(curr_dir)).get_template("atomtemplate.xml.j2").render(data).encode('utf-8'))

s3 = boto3.client('s3')
s3.upload_fileobj(output_atom, 'dyn.tedder.me', 'rss/ppa/rquillo.atom', ExtraArgs={
  'CacheControl': 'public, max-age=3600',
  'ContentType': 'application/atom+xml',
  'ACL': 'public-read',
  'StorageClass': 'REDUCED_REDUNDANCY'
})

#p = HTMLParser()
#p.feed(packages.text)


