#!/usr/bin/env python
"""
Synopsis:
    Generate Odoo model definitions.
    Write to models.py.
Usage:
    python gen_model.py [options]
Options:
    -f, --force
            Overwrite models.py and forms.py without asking.
    --no-class-suffixes
            Do not add suffix "_model" and _form" to generated class names.
    -h, --help
            Show this help message.
"""


from __future__ import print_function
import time
import sys
import os
import getopt
import importlib
if sys.version_info.major == 2:
    from StringIO import StringIO as stringio
else:
    from io import StringIO as stringio
from lxml import etree
from wrap_text import wrap_text
from collections import defaultdict

#
# Globals
#

supermod = None

# by default we sign XLM's with other tools, so we skip the Signature structure
SimpleType_skip = ['TTransformURI']
Class_skip = ['Signature', 'SignatureValue', 'SignedInfo',
              'Reference', 'DigestMethod', 'Transforms',
              'Transform', 'KeyInfo', 'X509Data',
              'CanonicalizationMethod', 'SignatureMethod']

#
# Classes
#


class ProgramOptions(object):
    def get_force_(self):
        return self.force_

    def set_force_(self, force):
        self.force_ = force
    force = property(get_force_, set_force_)


class Writer(object):
    def __init__(self, outfilename, stdout_also=False, mode='w'):
        self.outfilename = outfilename
        self.outfile = open(outfilename, mode)
        self.stdout_also = stdout_also
        self.line_count = 0

    def get_count(self):
        return self.line_count

    def get_outfilename(self):
        return self.outfilename

    def write(self, content):
        self.outfile.write(content)
        if self.stdout_also:
            sys.stdout.write(content)
        count = content.count('\n')
        self.line_count += count

    def close(self):
        self.outfile.close()


TEMPLATE_HEADER = """\
# Copyright 2019 Akretion - Raphael Valyi <raphael.valyi@akretion.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
# Generated {tstamp} by generateDS.py{version}.
# Python {pyversion}
#
import textwrap
from odoo import fields
from .. import spec_models
"""

#
# Functions
#

def generate_model(options, module_name):
    sys.path.append(options.output_dir)
    from generateds_definedsimpletypes import Defined_simple_type_table
    global supermod
    try:
        import generatedssuper
    except ImportError:
        import traceback
        traceback.print_exc()
        sys.exit(
            '\n* Error.  Cannot import generatedssuper.py.\n'
            'Make sure that the version of generatedssuper.py intended\n'
            'for Odoo support is first on your PYTHONPATH.\n'
        )
    if not hasattr(generatedssuper, 'Generate_DS_Super_Marker_'):
        sys.exit(
            '\n* Error.  Not the correct version of generatedssuper.py.\n'
            'Make sure that the version of generatedssuper.py intended\n'
            'for Odoo support is first on your PYTHONPATH.\n'
        )
    supermod = importlib.import_module(module_name)
    compact_version = options.version.replace('_', '')
    new_module_name = module_name.split("_%slib" % (compact_version,))[0]
    models_file_name = "%s/%s.py" % (options.output_dir, new_module_name)
    if (
            (os.path.exists(models_file_name)
            ) and
            not options.force):
        sys.stderr.write(
            '\nmodels.py exists.  '
            'Use -f/--force to overwrite.\n\n')
        sys.exit(1)
    models_writer = Writer(models_file_name)
    wrtmodels = models_writer.write
    version = options.output_dir.split('/')[-1]
    security_dir = os.path.abspath(os.path.join(options.output_dir,
                                                os.pardir, os.pardir,
                                                'security', version))
    security_writer = Writer("%s/%s" % (security_dir,
                             'ir.model.access.csv'), mode='a')
    wrtsecurity = security_writer.write
    unique_name_map = make_unique_name_map(supermod.__all__)

    tstamp = time.ctime()
    version = "(Akretion's branch)"
    current_working_directory = os.path.split(os.getcwd())[1]

    header = TEMPLATE_HEADER.format(
        tstamp=tstamp,
        version=version,
        pyversion=sys.version.replace('\n', ' '))
    wrtmodels(header)

    sys.path.append(options.path)
    generate_ds = importlib.import_module('generateDS')

    # collect implicit m2o related to explicit o2m:
    implicit_many2ones = defaultdict(list)
    simple_type_usages = defaultdict(list)
    for class_name in supermod.__all__:
        if hasattr(supermod, class_name):
            cls = getattr(supermod, class_name)
            for spec in cls.member_data_items_:
                if spec.get_container() == 1: # o2m
                    name = spec.get_name()
                    related = spec.get_data_type_chain()
                    if isinstance(related, list):
                        related = related[0]
                    implicit_many2ones[related].append((class_name, name))
                else:
                    data_type = spec.get_data_type()
                    if len(spec.get_data_type_chain()) == 0:
                        original_st = data_type
                    else:
                        original_st = spec.get_data_type_chain()[0]
                    if Defined_simple_type_table.get(original_st):
                        simple_type_usages[original_st].append(class_name)

    remapped_simple_types = {}
    for type_name in sorted(Defined_simple_type_table.keys()):
        if type_name in SimpleType_skip: # TODO see later
            continue
        descr = Defined_simple_type_table[type_name]
        if descr.get_enumeration_():
            enum = descr.get_enumeration_()

            if len(descr.get_descr_()) > 0:
                descr = "\n# ".join(wrap_text(descr.get_descr_(),
                                              0, 73, quote=False).splitlines())
                wrtmodels("\n# %s" % (descr,))
            
            usages = simple_type_usages[type_name]
            if len(usages) == 0:
                continue
            elif len(usages) == 1:
                old_name = type_name 
                name = type_name.split('Type')[0]
                type_name = "%s_%s" % (name,
                    simple_type_usages[type_name][0].split('Type')[0])
                remapped_simple_types[old_name] = type_name 
 
            wrtmodels('\n%s = [' % (type_name,))
            for i in enum:
                value = i[0][0:32] # FIXME for CCe, wrap it like label instead
                offset = len(value) + 10
                label = wrap_text(i[1], 5, 79, initial_indent=offset,
                                  multi=True, preserve_line_breaks=False)
                wrtmodels("""\n    ("%s", %s),""" % (value, label))
            wrtmodels("\n]\n")
            # wrtmodels("usages: %s\n" % (usages,))

    xsd = parse_preprocess_xsd(options)

    ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    type_nodes = xsd.xpath("//xs:complexType",
                           namespaces=ns)
    labels = {}
    for type_node in [t for t in type_nodes if t.attrib.get('name')]:
        labels[type_node.attrib['name']] = {}
        field_nodes = type_node.xpath(".//xs:element", namespaces=ns)
        for field in field_nodes:
            if field.attrib.get('name'):
                doc = field.xpath(".//xs:documentation",namespaces=ns)
                if len(doc) > 0:
                    spec_doc = str(doc[0].text)
                    labels[type_node.attrib['name']][field.attrib['name']] = spec_doc

    for class_name in supermod.__all__:
        if hasattr(supermod, class_name) and class_name.replace('Type','') not in Class_skip:
            cls = getattr(supermod, class_name)
            cls.generate_model_(
                wrtmodels, wrtsecurity, unique_name_map, options,
                generate_ds, implicit_many2ones, labels, Class_skip,
                remapped_simple_types, module_name)
    models_writer.close()
    print('Wrote %d lines to %s' % (models_writer.get_count(),
                                    models_writer.get_outfilename()))


def make_unique_name_map(name_list):
    """Make a mapping from names to names that are unique ignoring case."""
    unique_name_table = {}
    unique_name_set = set()
    for name in name_list:
        make_unique_name(name, unique_name_table, unique_name_set)
    return unique_name_table


def make_unique_name(name, unique_name_table, unique_name_set):
    """Create a name that is unique even when we ignore case."""
    new_name = name
    lower_name = new_name.lower()
    count = 0
    while lower_name in unique_name_set:
        count += 1
        new_name = '{}_{:d}'.format(name, count)
        lower_name = new_name.lower()
    unique_name_table[name] = new_name
    unique_name_set.add(lower_name)


def parse_preprocess_xsd(options):
    schema_file_name = os.path.join(
        os.path.abspath(os.path.curdir),
        options.infilename)
    infile = stringio()
    process_includes = importlib.import_module('process_includes')
    process_includes.process_include_files(
        options.infilename, infile,
        inpath=schema_file_name)
    infile.seek(0)

    doc = etree.parse(infile)
    return doc.getroot()


USAGE_TEXT = __doc__


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            args, 'hfs:d:l:x:p:s:', [
                'help', 'force', 'infilename',
                'no-class-suffixes', 'directory', 'path', 'schema'])
    except:
        usage()
    options = ProgramOptions()
    options.force = False
    options.class_suffixes = False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-f', '--force'):
            options.force = True
        elif opt == '--no-class-suffixes':
            options.class_suffixes = False
        elif opt in ('-p', '--path'):
            options.path = val
        elif opt in ('-d', '--directory'):
            options.output_dir = val
        elif opt in ('-s', '--infilename'):
            options.infilename = val
        elif opt in ('-l', '--schema_name'):
            options.schema_name = val
        elif opt in ('-x', '--version'):
            options.version = val
    if len(args) != 1:
        usage()
    module_name = args[0]
    options.module_name = module_name
    generate_model(options, module_name)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #import ipdb; ipdb.set_trace()
    main()
