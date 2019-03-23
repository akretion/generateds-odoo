from  __future__ import print_function
import sys
from generateds_definedsimpletypes import Defined_simple_type_table
from wrap_text import wrap_text

#
# Globals

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_Marker_ = None

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
    'float': None,
    'double': None,
}
Decimal_type_table = {
    'decimal': None,
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
    def extract_string_help_select(cls, field_name, doc):
        help_attr = None
        string = field_name
        if doc:
            string = ' '.join(doc.strip().splitlines()[0].split())
            if len(string) > 36 and len(string.split(". ")[0]) < 64:
                string = string.split(". ")[0].strip()
            if len(string) > 36 and len(string.split(", ")[0]) < 64:
                string = string.split(", ")[0].strip()
            if len(string) > 36 and len(string.split(" (")[0]) < 64:
                string = string.split(" (")[0].strip()
            if len(string) > 36 and len(string.split("-")[0]) < 64: # TODO sure?
                string = string.split("-")[0].strip()
            if len(string) > 36 and len(string.split(".")[0]) < 64:
                string = string.split(".")[0].strip()
            if len(string) > 36 and len(string.split(",")[0]) < 64:
                string = string.split(",")[0].strip()
            string = string.replace("\"", "'")
            if string.endswith(':'):
                string = string[:-1]
            if len(string) > 58:
                string = field_name

            if string != doc and string != doc[:-1]:
                # help is only useful it adds more than a ponctuation symbol
                doc = wrap_text(doc, 8, 78, initial_indent=14, multi=True)
                help_attr = 'help=%s' % (doc)
        return string, help_attr

    @classmethod
    def generate_model_(
            cls, wrtmodels, wrtsecurity, unique_name_map, options,
            generate_ds, implicit_many2ones, labels, class_skip,
            remapped_simple_types):

        # we pass the generateDS package as an argument to avoid
        # having to import it dynamically from a custom location
        # multiple times
        mapName = generate_ds.mapName
        cleanupName = generate_ds.cleanupName
        AnyTypeIdentifier = generate_ds.AnyTypeIdentifier

        class_suffixes = options.class_suffixes
        Lib_name = options.schema_name
        Version = options.version
        if class_suffixes:
            model_suffix = '_model'
        else:
            model_suffix = ''

        # TODO via options
        Date_type_table.update({'TData': None})
        DateTime_type_table.update({'TDateTimeUTC': None})
        Simple_type_table.update(Date_type_table)
        Simple_type_table.update(DateTime_type_table)
        #wrtmodels("%s" % (Simple_type_table,))

        class_name = unique_name_map.get(cls.__name__)
        odoo_class_name = class_name.replace('Type', '')
        odoo_class = odoo_class_name[0].capitalize() + odoo_class_name[1:100]
        # TODO regexp replace
#        field_prefix = "%s_%s__" % (Lib_name, odoo_class_name.lower())
        field_prefix = "%s_" % (Lib_name,)

        wrtmodels('\n\nclass %s%s(spec_models.AbstractSpecMixin):\n' % (
            odoo_class, model_suffix, ))
        if cls.__doc__:
            wrtmodels('    %s\n' % (
                wrap_text(cls.__doc__, 4, 79), ))
            # setting _description with docstring avoids re-splitting
            # doc lines again once they were formated for the Python lib
            wrtmodels("    _description = textwrap.dedent(\"    %s\" % (__doc__,))\n")
        else:
            wrtmodels("    _description = '%s'\n" % (odoo_class_name.lower()))
        wrtmodels("    _name = '%s.%s.%s'\n" % (Lib_name, Version,
                                                odoo_class_name.lower(), ))
        wrtmodels("    _generateds_type = '%s'\n" % (cls.__name__))
        wrtmodels("    _concrete_rec_name = '%s_%s'\n\n" %
                  (Lib_name, cls.member_data_items_[0].get_name()))
        wrtsecurity("access_%s_%s_%s,%s.%s.%s,model_%s_%s_%s,base.group_user,1,1,1,1\n" % (
        Lib_name, Version, odoo_class_name.lower(),
        Lib_name, Version, odoo_class_name.lower(),
        Lib_name, Version, odoo_class_name.lower().replace('.', '_')))
#        if cls.superclass is not None:
#            wrtmodels('    %s = models.ForeignKey("%s%s")\n' % (
#                cls.superclass.__name__, cls.superclass.__name__,
#                model_suffix, ))

        if class_name in implicit_many2ones:
            comodel = implicit_many2ones[class_name][0][0].replace("Type", "")
            target_field = implicit_many2ones[class_name][0][1]
            wrtmodels(
                '    %s%s_%s_id = fields.Many2one(\n        "%s.%s.%s")\n' % (
                    field_prefix, target_field, comodel, Lib_name, Version,
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
                          field_prefix, k,)) # TODO duplicate name?
#            for i in v:
#                wrtmodels("\n        ('%s%s', '%s')," % (field_prefix, i, i))

            items = ",\n        ".join(
                ["('%s%s', '%s')" % (field_prefix, i, i) for i in v])
            wrtmodels("\n        %s" % (items,))
            label="/".join(i for i in v)
            if len(label) > 50:
                label="%s..." % (label[0:50])
            wrtmodels("""],\n        "%s",\n        default="%s%s")\n""" % (
                label, field_prefix, v[0]))

        for spec in cls.member_data_items_:
            name = spec.get_name()
            choice = spec.get_choice()
            prefix, name = cls.get_prefix_name(name)
            data_type = spec.get_data_type()
            is_optional = spec.get_optional()
            prefix, data_type = cls.get_prefix_name(data_type)
            if labels.get(class_name) and labels[class_name].get(name):
                spec_doc = labels[class_name][name]
            else:
                spec_doc = name
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
            string, help_attr = cls.extract_string_help_select(
                spec.get_name(), spec_doc)

            if is_optional:
                options = 'string="%s"' % (string,)
            else:
                if (len(string) + len(field_name) > 30):
                    options = 'string="%s",\n        xsd_required=True' % (
                        string,)
                else:
                    options = 'string="%s", xsd_required=True' % (string,)

            if choice != None:
                options = """choice='%s',\n        %s""" % (choice, options)

            options_nohelp = options
            if help_attr:
                options = "%s,\n        %s" % (options, help_attr,)

            if len(spec.get_data_type_chain()) == 0:
                original_st = data_type
            else:
                original_st = spec.get_data_type_chain()[0]

            if data_type in Simple_type_table:
                if data_type in Integer_type_table:
                    wrtmodels('    %s = fields.Integer(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in Float_type_table:
                    wrtmodels('    %s = fields.Float(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in Decimal_type_table or 'TDec_' in original_st:
                    if 'TDec_' in original_st:  # TODO make more flexible
                        digits = original_st[8]
                        if len(string) > 50:
                            options = "\n        %s" % (options,)
                            options = "digits=%s,%s" % (digits, options)
                        else:
                            options = "digits=%s, %s" % (digits, options)
                    wrtmodels(
                        '    %s = fields.Monetary(\n        %s)\n' % (
                            field_name, options))
                elif data_type in Date_type_table\
                        or original_st in Date_type_table:
                    wrtmodels('    %s = fields.Date(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in DateTime_type_table\
                        or original_st in DateTime_type_table:
                    wrtmodels('    %s = fields.Datetime(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in Time_type_table:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        field_name, data_type, ))
                    wrtmodels('    %s = fields.TimeField(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in Boolean_type_table:
                    wrtmodels('    %s = fields.Boolean(\n        %s)\n' % (
                        field_name, options, ))
                elif data_type in String_type_table:
                   if Defined_simple_type_table.get(original_st) \
                            and (Defined_simple_type_table[original_st]
                            ).get_enumeration_():
                        if remapped_simple_types.get(original_st):
                            enum_const = remapped_simple_types[original_st]
                        else:
                            enum_const = original_st
                        enum_type = Defined_simple_type_table[original_st]
                        string, help_attr = cls.extract_string_help_select(
                           field_name,
                           enum_type.get_descr_() or spec_doc)
                        if help_attr:
                            options = "%s,\n        %s" % (options_nohelp,
                                                           help_attr)
                        wrtmodels(
                            '    %s = fields.Selection(\n        %s,\n        %s)\n' % (
                            field_name, enum_const, options, ))
                   else:
#                        if len(string) + len(field_name) > 51:
                        options = "\n        %s" % (options,)
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
                    if clean_data_type in class_skip:
                        continue
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
                    '        "%s_%s_id",\n' % (
                        field_name, odoo_class_name))
                    wrtmodels(
                        "        %s\n" % (options,))
                    # NOTE can we force at least one unless is_optional?

                    wrtmodels('    )\n')
