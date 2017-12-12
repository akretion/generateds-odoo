
from __future__ import print_function
import sys
from generateds_definedsimpletypes import Defined_simple_type_table
from generateDS import AnyTypeIdentifier, mapName, cleanupName

#
# Globals

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_Marker_ = None

Lib_name = 'nfe'
Version = 'v3_10'

#
# Tables of builtin types
Simple_type_table = {
    'string': None,
    'normalizedString': None,
    'token': None,
    'base64Binary': None,
    'hexBinary': None,
    'integer': None,
    'positiveInteger': None,
    'negativeInteger': None,
    'nonNegativeInteger': None,
    'nonPositiveInteger': None,
    'long': None,
    'unsignedLong': None,
    'int': None,
    'unsignedInt': None,
    'short': None,
    'unsignedShort': None,
    'byte': None,
    'unsignedByte': None,
    'decimal': None,
    'float': None,
    'double': None,
    'boolean': None,
    'duration': None,
    'dateTime': None,
    'date': None,
    'time': None,
    'gYear': None,
    'gYearMonth': None,
    'gMonth': None,
    'gMonthDay': None,
    'gDay': None,
    'Name': None,
    'QName': None,
    'NCName': None,
    'anyURI': None,
    'language': None,
    'ID': None,
    'IDREF': None,
    'IDREFS': None,
    'ENTITY': None,
    'ENTITIES': None,
    'NOTATION': None,
    'NMTOKEN': None,
    'NMTOKENS': None,
}
Integer_type_table = {
    'integer': None,
    'positiveInteger': None,
    'negativeInteger': None,
    'nonNegativeInteger': None,
    'nonPositiveInteger': None,
    'long': None,
    'unsignedLong': None,
    'int': None,
    'unsignedInt': None,
    'short': None,
    'unsignedShort': None,
}
Float_type_table = {
    'decimal': None,
    'float': None,
    'double': None,
}
String_type_table = {
    'string': None,
    'normalizedString': None,
    'token': None,
    'NCName': None,
    'ID': None,
    'IDREF': None,
    'IDREFS': None,
    'ENTITY': None,
    'ENTITIES': None,
    'NOTATION': None,
    'NMTOKEN': None,
    'NMTOKENS': None,
    'QName': None,
    'anyURI': None,
    'base64Binary': None,
    'hexBinary': None,
    'duration': None,
    'Name': None,
    'language': None,
}
Date_type_table = {
    'date': None,
    'gYear': None,
    'gYearMonth': None,
    'gMonth': None,
    'gMonthDay': None,
    'gDay': None,
}
DateTime_type_table = {
    'dateTime': None,
}
Time_type_table = {
    'time': None,
}
Boolean_type_table = {
    'boolean': None,
}


#
# Classes

class GeneratedsSuper(object):
    def gds_format_string(self, input_data, input_name=''):
        return input_data

    def gds_format_integer(self, input_data, input_name=''):
        return '%d' % input_data

    def gds_format_float(self, input_data, input_name=''):
        return '%f' % input_data

    def gds_format_double(self, input_data, input_name=''):
        return '%e' % input_data

    def gds_format_boolean(self, input_data, input_name=''):
        return '%s' % input_data

    def gds_str_lower(self, instring):
        return instring.lower()

    @classmethod
    def get_prefix_name(cls, tag):
        prefix = ''
        name = ''
        items = tag.split(':')
        if len(items) == 2:
            prefix = items[0]
            name = items[1]
        elif len(items) == 1:
            name = items[0]
        return prefix, name

    @classmethod
    def extract_string_help_select(cls, spec):
        string = spec.get_name()
        help_attr = None
        if spec.get_documentation():
            doc = spec.get_documentation()
            help_attr = 'help="""%s"""' % (doc)
            if len(doc) < 64: # then use help for string
                string = doc
            elif len(doc.split(".")[0]) < 64:
                string = doc.split(".")[0]
            elif len(doc.split(",")[0]) < 64:
                string = doc.split(",")[0]
            elif len(doc.split("-")[0]) < 64:
                string = doc.split("-")[0]
        return string, help_attr, [] # TODO extract possible select options

    @classmethod
    def generate_model_(
            cls, wrtmodels, unique_name_map, class_suffixes,
            implicit_many2ones):
        if class_suffixes:
            model_suffix = '_model'
        else:
            model_suffix = ''
        class_name = unique_name_map.get(cls.__name__)
        odoo_class_name = class_name.replace('Type', '')
        # TODO regexp replace
        field_prefix = "%s_%s__" % (Lib_name, odoo_class_name.lower())

        wrtmodels('\nclass %s%s(sped.SpedBase):\n' % (
            odoo_class_name, model_suffix, ))
        if cls.__doc__:
            wrtmodels('    _description = """%s"""\n' % (cls.__doc__, ))
        wrtmodels("    _name = '%s.%s.%s'\n" % (Lib_name, Version,
                                                odoo_class_name.lower(), ))
        wrtmodels("    _generateds_type = '%s'\n" % (cls.__name__))
        wrtmodels("    _concrete_impls = []\n\n")
#        if cls.superclass is not None:
#            wrtmodels('    %s = models.ForeignKey("%s%s")\n' % (
#                cls.superclass.__name__, cls.superclass.__name__,
#                model_suffix, ))

        if class_name in implicit_many2ones:
            comodel = implicit_many2ones[class_name][0][0]
            target_field = implicit_many2ones[class_name][0][1]
            wrtmodels(
                            '    %s%s_%s_id = fields.Many2one("%s.%s.%s")\n' % (
                                field_prefix, comodel, target_field, Lib_name, Version,
                                comodel.lower()))

        choice_selectors = {}
        for spec in cls.member_data_items_:
            name = spec.get_name()
            choice = spec.get_choice()
            if choice != None:
                if choice not in choice_selectors.keys():
                    choice_selectors[choice] = []
                choice_selectors[choice].append(name)
        for k, v in choice_selectors.items():
            # TODO can we have a better label?
            wrtmodels(
                      """    %schoice%s = fields.Selection([""" % (
                          field_prefix, k,))
            for i in v:
                wrtmodels("""\n        (%s%s, %s),""" % (field_prefix, i, i))
            label="/".join(i for i in v)
            wrtmodels("""],\n        "%s",\n        default="%s%s")\n""" % (
                label, field_prefix, v[0]))

        for spec in cls.member_data_items_:
            name = spec.get_name()
            choice = spec.get_choice()
            prefix, name = cls.get_prefix_name(name)
            data_type = spec.get_data_type()
            is_optional = spec.get_optional()
            prefix, data_type = cls.get_prefix_name(data_type)
            if data_type in Defined_simple_type_table:
                data_type = (Defined_simple_type_table[data_type]
                             ).get_type_name_()
            name = mapName(cleanupName(name))
            if name == 'id':
                name += 'x'
            elif name.endswith('_') and not name == AnyTypeIdentifier:
                name += 'x'
            field_name = "%s%s" % (field_prefix, name)
            clean_data_type = mapName(cleanupName(data_type))
            if data_type == AnyTypeIdentifier:
                data_type = 'string'
            string, help_attr, select = cls.extract_string_help_select(spec)

            if is_optional:
                options = 'string="""%s"""' % (string,)
            else:
                options = 'string="""%s""", xsd_required=True' % (string,)

            if choice != None:
                options = """choice='%s',\n        %s""" % (choice, options)

            if help_attr:
                options = "%s,\n        %s" % (options, help_attr,)

            if data_type in Simple_type_table:
                if data_type in Integer_type_table:
                    wrtmodels('    %s = fields.Integer(%s)\n' % (
                        field_name, options, ))
                elif data_type in Float_type_table:
                    wrtmodels('    %s = fields.Float(%s)\n' % (
                        field_name, options, ))
                elif data_type in Date_type_table:
                    wrtmodels('    %s = fields.Date(%s)\n' % (
                        field_name, options, ))
                elif data_type in DateTime_type_table:
                    wrtmodels('    %s = fields.Datetime(%s)\n' % (
                        field_name, options, ))
                elif data_type in Time_type_table:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        field_name, data_type, ))
                    wrtmodels('    %s = fields.TimeField(%s)\n' % (
                        field_name, options, ))
                elif data_type in Boolean_type_table:
                    wrtmodels('    %s = fields.Boolean(%s)\n' % (
                        field_name, options, ))
                elif data_type in String_type_table:
                    if len(spec.get_data_type_chain()) == 0:
                        original_st = data_type
                    else:
                        original_st = spec.get_data_type_chain()[0]
                    if 'TDec_' in original_st:
                        digits = original_st[8]
                        options = "digits=%s,\n        %s" % (digits, options)
                        wrtmodels(
                            '    %s = fields.Monetary(%s)\n' % (
                                field_name, options, ))
                    elif Defined_simple_type_table.get(original_st) \
                        and (Defined_simple_type_table[original_st]
                             ).get_enumeration_():
                            enum_type = Defined_simple_type_table[original_st]
                            enum = enum_type.get_enumeration_()
                            wrtmodels(
                                '    %s = fields.Selection(%s,\n        %s)\n' % (
                                field_name, original_st, options, ))
                    else:
                        wrtmodels(
                            '    %s = fields.Char(%s)\n' % (
                                field_name, options, )) # TODO size
                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        name, data_type, ))

            elif not Defined_simple_type_table.get(data_type):
                mapped_type = unique_name_map.get(clean_data_type)
                if mapped_type is not None:
                    clean_data_type = mapped_type.replace('Type', '')
                    # TODO regexp replace
                if spec.get_container() == 0: # name in cls._many2one:
                    wrtmodels(
                    '    %s = fields.Many2one(\n        "%s.%s.%s",\n' % (
                                field_name, Lib_name, Version,
                                clean_data_type.lower()))
                    wrtmodels(
                        "        %s)\n" % (options))
                    # TODO is ondelete='cascade' really the exception?
                else:
                    wrtmodels(
                    '    %s = fields.One2many(\n        "%s.%s.%s",\n' % (
                        field_name, Lib_name, Version, clean_data_type.lower()))
                    wrtmodels(
                    '        "%s_%s__%s_%s_id",\n' % (
                        Lib_name, clean_data_type.lower(), field_name,
                        odoo_class_name))
                    wrtmodels(
                        "        %s\n" % (options,))
                    # NOTE can we force at least one unless is_optional?

                    wrtmodels('    )\n')
        wrtmodels('\n')
