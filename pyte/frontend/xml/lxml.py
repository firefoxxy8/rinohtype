
import os

from lxml import etree, objectify

from ...util import all_subclasses
from . import CATALOG_URL


try:
    os.environ['XML_CATALOG_FILES'] += ' ' + CATALOG_URL
except KeyError:
    os.environ['XML_CATALOG_FILES'] = CATALOG_URL


class Parser(object):
    def __init__(self, namespace, schema=None):
        lookup = etree.ElementNamespaceClassLookup()
        namespace = lookup.get_namespace(namespace)
        namespace[None] = self.element_class
        namespace.update({cls.__name__.lower(): cls
                          for cls in all_subclasses(self.element_class)})
        self.parser = objectify.makeparser(remove_comments=True,
                                           no_network=True)
        self.parser.set_element_class_lookup(lookup)
        self.schema = etree.RelaxNG(etree.parse(schema))

    def parse(self, xmlfile):
        xml = objectify.parse(xmlfile, self.parser)#, base_url=".")
        xml.xinclude()
        if not self.schema.validate(xml):
            err = self.schema.error_log
            raise Exception("XML file didn't pass schema validation:\n%s" % err)
        return xml


class BaseElement(objectify.ObjectifiedElement):
    @property
    def filename_and_line(self):
        return self.getroottree().docinfo.URL, self.sourceline
