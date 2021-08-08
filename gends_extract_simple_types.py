#!/usr/bin/env python3

#
# Imports

from __future__ import print_function

import argparse
import os
import sys
from importlib import import_module

from lxml import etree

if sys.version_info.major == 2:
    from StringIO import StringIO as stringio
else:
    from io import StringIO as stringio


#
# Globals and constants

SchemaNS = "http://www.w3.org/2001/XMLSchema"
Nsmap = {
    "xs": SchemaNS,
}


#
# Functions for external use


#
# Classes


class TypeDescriptor(object):
    def __init__(self, name, type_name=None, descr=None):
        self.name_ = name
        self.type_name_ = type_name
        self.type_obj_ = None
        self.descr_ = descr

    def __str__(self):
        return "<{} -- name: {} type: {}>".format(
            self.__class__.__name__,
            self.name,
            self.type_name,
        )

    def get_name_(self):
        return self.name_

    def set_name_(self, name):
        self.name_ = name

    name = property(get_name_, set_name_)

    def get_descr_(self):
        return self.descr_

    def get_type_name_(self):
        return self.type_name_

    def set_type_name_(self, type_name):
        self.type_name_ = type_name

    type_name = property(get_type_name_, set_type_name_)

    def get_type_obj_(self):
        return self.type_obj_

    def set_type_obj_(self, type_obj):
        self.type_obj_ = type_obj

    type_obj = property(get_type_obj_, set_type_obj_)


class ComplexTypeDescriptor(TypeDescriptor):
    def __init__(self, name):
        super(ComplexTypeDescriptor, self).__init__(name)
        self.elements_ = []
        self.attributes_ = {}

    def get_elements_(self):
        return self.elements_

    def set_elements_(self, elements):
        self.elements_ = elements

    elements = property(get_elements_, set_elements_)

    def get_attributes_(self):
        return self.attributes_

    def set_attributes_(self, attributes):
        self.attributes_ = attributes

    attributes = property(get_attributes_, set_attributes_)


class SimpleTypeDescriptor(TypeDescriptor):
    def __init__(self, name, type_name, enum=None, descr=None):
        self.enumeration_ = enum
        super(SimpleTypeDescriptor, self).__init__(name, type_name, descr)

    def get_enumeration_(self):
        return self.enumeration_


Header_template = """
# -*- coding: utf-8 -*-


class TypeDescriptor(object):
    def __init__(self, name, type_name=None, descr=None):
        self.name_ = name
        self.type_name_ = type_name
        self.type_obj_ = None
        self.descr_ = descr
    def __str__(self):
        return '<%s -- name: %s type: %s>' % (self.__class__.__name__,
            self.name, self.type_name,)
    def get_name_(self):
        return self.name_
    def set_name_(self, name):
        self.name_ = name
    name = property(get_name_, set_name_)
    def get_descr_(self):
        return self.descr_
    def get_type_name_(self):
        return self.type_name_
    def set_type_name_(self, type_name):
        self.type_name_ = type_name
    type_name = property(get_type_name_, set_type_name_)
    def get_type_obj_(self):
        return self.type_obj_
    def set_type_obj_(self, type_obj):
        self.type_obj_ = type_obj
    type_obj = property(get_type_obj_, set_type_obj_)

class ComplexTypeDescriptor(TypeDescriptor):
    def __init__(self, name):
        super(ComplexTypeDescriptor, self).__init__(name)
        self.elements_ = []
        self.attributes_ = {}
    def get_elements_(self):
        return self.elements_
    def set_elements_(self, elements):
        self.elements_ = elements
    elements = property(get_elements_, set_elements_)
    def get_attributes_(self):
        return self.attributes_
    def set_attributes_(self, attributes):
        self.attributes_ = attributes
    attributes = property(get_attributes_, set_attributes_)

class SimpleTypeDescriptor(TypeDescriptor):
    def __init__(self, name, type_name, enum=None, descr=None):
        self.enumeration_ = enum
        super(SimpleTypeDescriptor, self).__init__(name, type_name, descr)

    def get_enumeration_(self):
        return self.enumeration_
"""


#
# Table of builtin types
Simple_type_names = [
    "string",
    "normalizedString",
    "token",
    "base64Binary",
    "hexBinary",
    "integer",
    "positiveInteger",
    "negativeInteger",
    "nonNegativeInteger",
    "nonPositiveInteger",
    "long",
    "unsignedLong",
    "int",
    "unsignedInt",
    "short",
    "unsignedShort",
    "byte",
    "unsignedByte",
    "decimal",
    "float",
    "double",
    "boolean",
    "duration",
    "dateTime",
    "date",
    "time",
    "gYear",
    "gYearMonth",
    "gMonth",
    "gMonthDay",
    "gDay",
    "Name",
    "QName",
    "NCName",
    "anyURI",
    "language",
    "ID",
    "IDREF",
    "IDREFS",
    "ENTITY",
    "ENTITIES",
    "NOTATION",
    "NMTOKEN",
    "NMTOKENS",
]

Builtin_descriptors = {}
for name in Simple_type_names:
    Builtin_descriptors[name] = SimpleTypeDescriptor(name, name)


#
# Functions for internal use and testing


def extract_descriptors(args):
    if os.path.exists(args.outfilename) and not args.force:
        sys.stderr.write(
            "\nFile {} exists.  Use -f/--force to overwrite.\n\n".format(
                args.outfilename
            )
        )
        sys.exit(1)
    outfile = open(args.outfilename, "w")

    schema_file_name = os.path.join(os.path.abspath(os.path.curdir), args.infilename)
    infile = stringio()
    sys.path.append(args.path)
    process_includes = import_module("process_includes")
    process_includes.process_include_files(
        args.infilename, infile, inpath=schema_file_name
    )
    infile.seek(0)

    doc = etree.parse(infile)
    root = doc.getroot()
    descriptors = {}
    extract(root, descriptors, outfile)
    for descriptor in list(descriptors.values()):
        descriptor.export(outfile)
    outfile.close()


def get_descriptor_name(d):
    return d.name


def extract(root, descriptors, outfile):
    unresolved = {}
    # Process top level simpleTypes.  Resolve the base types.
    nodes = root.xpath("xs:simpleType", namespaces=Nsmap)
    # TODO get parent and if it is schema (or via import),
    # then offer an option to export it in a common file
    for node in nodes:
        name, type_name, enum, descr = get_simple_name_type(node)
        descriptor = SimpleTypeDescriptor(name, type_name, enum, descr)
        unresolved[name] = descriptor
    resolved = resolve_simple_types(unresolved)
    export_defined_simple_types(outfile, resolved)


##     for descriptor in resolved.itervalues():
##         print '%s  type name: %s' % (descriptor, descriptor.type_obj.name, )


def export_defined_simple_types(outfile, resolved):
    wrt = outfile.write
    wrt(Header_template)
    wrt("Defined_simple_type_table = {\n")
    for descriptor in list(resolved.values()):
        name = descriptor.name
        prefix, type_name = get_prefix_name(descriptor.type_name)
        if descriptor.get_enumeration_():
            wrt(
                """    '%s': SimpleTypeDescriptor('%s', '%s',
        %s,
        \"\"\"%s\"\"\"),\n"""
                % (
                    name,
                    name,
                    type_name,
                    descriptor.get_enumeration_(),
                    descriptor.get_descr_(),
                )
            )
        else:
            wrt(
                "    '%s': SimpleTypeDescriptor('%s', '%s'),\n"
                % (name, name, type_name)
            )
    wrt("}\n\n")


def resolve_simple_types(unresolved):
    resolved = {}
    # import pdb; pdb.set_trace()
    sorted_descriptors = list(unresolved.values())
    sorted_descriptors.sort(key=get_descriptor_name)
    for descriptor in sorted_descriptors:
        resolve_1_simple_type(descriptor, resolved, unresolved)
    return resolved


def resolve_1_simple_type(descriptor, resolved, unresolved):
    prefix, name = get_prefix_name(descriptor.type_name)
    if name in Builtin_descriptors:
        type_obj = Builtin_descriptors[name]
        descriptor.type_obj = type_obj
        resolved[descriptor.name] = descriptor
        return type_obj
    elif name in resolved:
        type_obj = resolved[name].type_obj
        descriptor.type_obj = type_obj
        resolved[descriptor.name] = descriptor
        return type_obj
    else:
        type_name = descriptor.type_name
        if type_name not in unresolved:
            # If we can't find it, try after stripping off namespace prefix.
            type_name = type_name.split(":")[-1]
            if type_name not in unresolved:
                raise etree.XmlSchemaError(
                    "Can't find simple type (%s) in unresolved types." % (type_name)
                )
        type_obj = resolve_1_simple_type(unresolved[type_name], resolved, unresolved)
        descriptor.type_obj = type_obj
        resolved[descriptor.name] = descriptor
    return type_obj


def get_simple_name_type(node):
    type_name = None
    name = node.get("name")
    enumeration = None
    description = ""

    descriptions = node.xpath(
        "./xs:annotation/xs:documentation/text()", namespaces=Nsmap
    )

    if descriptions:
        description = descriptions[0]

    else:
        # eventually the description is not carried by the SimpleType
        # but by its parent element. When the SimpleType is used only in
        # a specific element we can use the element description
        elements = node.xpath("//*[@type='{}']".format(name), namespaces=Nsmap)
        if len(elements) == 1:
            descriptions = elements[0].xpath(
                "./xs:annotation/xs:documentation/text()", namespaces=Nsmap
            )

            if descriptions:
                description = descriptions[0]

    # Is it a restriction?
    if name is not None:
        nodes = node.xpath(".//xs:restriction", namespaces=Nsmap)
        if nodes:
            restriction = nodes[0]
            type_name = restriction.get("base")
            for restriction in nodes:
                values = restriction.xpath("./xs:enumeration/@value", namespaces=Nsmap)
                if values:
                    enumeration = [(v.strip(), v.strip()) for v in values]

                    # now we try to read enum labels from the doc annotation:
                    enum = list(reversed(enumeration))
                    enum2 = []
                    if len(description) > 0:
                        descr = description.strip()

                        # first we try to see if there could be 1 label per line
                        lines = descr.splitlines()
                        descr_size = len(lines)

                        # else we try to split with ";"
                        if descr_size < len(enum) and ":" in description:
                            split = description.split(":")
                            lines = [split[0]] + split[1].split(";")
                            descr = "\n".join(lines)
                            descr_size = len(lines)

                        if descr_size >= len(enum):
                            # case where labels on each line
                            i = 0
                            for l in reversed(lines):
                                l = l.strip()
                                if not l.startswith(enum[i][0]):
                                    break
                                else:
                                    if l.endswith(";"):
                                        l = l[0 : len(l) - 1]
                                    enum2.append((enum[i][0], l))
                                if len(enum2) == len(enum):
                                    break
                                i += 1

                        if len(enum2) == len(enum):
                            description = "\n".join(lines[0 : descr_size - i - 1])
                            enumeration = list(reversed(enum2))
                        else:
                            description = "\n".join([l.strip() for l in lines])

    # Not a restriction.  Try list.
    if type_name is None:
        nodes = node.xpath(".//xs:list", namespaces=Nsmap)
        if nodes:
            type_name = "string"
    # Not a list.  Try union.
    if type_name is None:
        nodes = node.xpath(".//xs:union", namespaces=Nsmap)
        if nodes:
            union = nodes[0]
            member_types = union.get("memberTypes")
            if member_types:
                member_types = member_types.split()
                if member_types:
                    type_name = member_types[0]
    return name, type_name, enumeration, description


def get_prefix_name(tag):
    prefix = ""
    name = ""
    items = tag.split(":")
    if len(items) == 2:
        prefix = items[0]
        name = items[1]
    elif len(items) == 1:
        name = items[0]
    return prefix, name


def etxpath(node, pat):
    nodes = node.xpath(pat, namespaces=Nsmap)
    return nodes


USAGE_TEXT = __doc__


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


USAGE_TEXT = """synopsis: capture XML Schema simpleType descriptors
"""


def main():
    parser = argparse.ArgumentParser(description=USAGE_TEXT)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show additional info"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force overwrite of output file without asking",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)),
        help="path to generateDS folder",
    )
    parser.add_argument("infilename", type=str, help="input XML Schema file")
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        dest="outfilename",
        default="generateds_definedsimpletypes.py",
        help="output (.py) file name",
    )
    args = parser.parse_args()
    extract_descriptors(args)


if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    main()
