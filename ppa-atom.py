#!/usr/bin/python

#from HTMLParser import HTMLParser
import requests
from lxml import html
import jinja2
import boto

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
  data['items'].append( (
    rowstrs[0][0],
    URL,
    ' '.join( (rowstrs) )
  ))


# idea stolen from codeape on stackoverflow: http://stackoverflow.com/a/2101186/659298
output_atom = jinja2.Environment(loader=jinja2.FileSystemLoader(".")).get_template("atomtemplate.xml.j2").render(data)

s3 = boto.connect_s3()
s3key = s3.get_bucket('tedder').new_key('rss/ppa/rquillo.atom')
s3key.set_metadata('Content-Type', 'application/atom+xml')
s3key.set_contents_from_string(output_atom, replace=True, reduced_redundancy=True, headers={'Cache-Control':'public, max-age=3600'}, policy="public-read")

print "output at: http://tedder.me/rss/ppa/rquillo.atom"

#p = HTMLParser()
#p.feed(packages.text)


