"""
Module for processing Sitemaps.

Note: The main purpose of this module is to provide support for the
SitemapSpider, its API is subject to change without notice.
"""

from cStringIO import StringIO
from xml.etree.cElementTree import ElementTree

class Sitemap(object):
    """Class to parse Sitemap (type=urlset) and Sitemap Index
    (type=sitemapindex) files"""

    def __init__(self, xmltext):
        tree = ElementTree()
        tree.parse(StringIO(xmltext))
        self._root = tree.getroot()
        _, self.type = self._root.tag.split('}', 1)

    def __iter__(self):
        for elem in self._root.getchildren():
            d = {}
            for el in elem.getchildren():
                _, name = el.tag.split('}', 1)
                d[name] = el.text
            yield d

def sitemap_urls_from_robots(robots_text):
    """Return an iterator over all sitemap urls contained in the given
    robots.txt file
    """
    for line in robots_text.splitlines():
        if line.lstrip().startswith('Sitemap:'):
            yield line.split(':', 1)[1].strip()
