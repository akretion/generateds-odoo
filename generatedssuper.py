from __future__ import print_function

import re
import sys

from generateds_definedsimpletypes import Defined_simple_type_table
# from odoo.wrap_text import wrap_text
from wrap_text import wrap_text

#
# Globals

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_Marker_ = None

#
# Tables of builtin types
Integer_type_table = {
    "integer": None,
    "positiveInteger": None,
    "negativeInteger": None,
    "nonNegativeInteger": None,
    "nonPositiveInteger": None,
    "long": None,
    "unsignedLong": None,
    "int": None,
    "unsignedInt": None,
    "short": None,
    "unsignedShort": None,
}
Float_type_table = {
    "float": None,
    "double": None,
}
Decimal_type_table = {
    "decimal": None,
}
String_type_table = {
    "string": None,
    "normalizedString": None,
    "token": None,
    "NCName": None,
    "ID": None,
    "IDREF": None,
    "IDREFS": None,
    "ENTITY": None,
    "ENTITIES": None,
    "NOTATION": None,
    "NMTOKEN": None,
    "NMTOKENS": None,
    "QName": None,
    "anyURI": None,
    "base64Binary": None,
    "hexBinary": None,
    "duration": None,
    "Name": None,
    "language": None,
}
Date_type_table = {
    "date": None,
    "gYear": None,
    "gYearMonth": None,
    "gMonth": None,
    "gMonthDay": None,
    "gDay": None,
}
DateTime_type_table = {
    "dateTime": None,
}
Time_type_table = {
    "time": None,
}
Boolean_type_table = {
    "boolean": None,
}
Simple_type_table = {
    "byte": None,
    "unsignedByte": None,
}
Simple_type_table.update(Integer_type_table)
Simple_type_table.update(Float_type_table)
Simple_type_table.update(Decimal_type_table)
Simple_type_table.update(String_type_table)
Simple_type_table.update(Date_type_table)
Simple_type_table.update(DateTime_type_table)
Simple_type_table.update(Time_type_table)
Simple_type_table.update(Boolean_type_table)

MONETARY_DIGITS = 2

#
# Classes


class GeneratedsSuper(object):
    def gds_format_string(self, input_data, input_name=""):
        return input_data

    def gds_format_integer(self, input_data, input_name=""):
        return "%d" % input_data

    def gds_format_float(self, input_data, input_name=""):
        return "%f" % input_data

    def gds_format_double(self, input_data, input_name=""):
        return "%e" % input_data

    def gds_format_boolean(self, input_data, input_name=""):
        return "%s" % input_data

    def gds_str_lower(self, instring):
        return instring.lower()

    @classmethod
    def get_prefix_name(cls, tag):
        prefix = ""
        name = ""
        items = tag.split(":")
        if len(items) == 2:
            prefix = items[0]
            name = items[1]
        elif len(items) == 1:
            name = items[0]
        return prefix, name

    @classmethod
    def extract_string_help_select(cls, field_name, doc, unique_labels):
        help_attr = None
        string = field_name
        if doc:
            string = " ".join(doc.strip().splitlines()[0].split())
            if len(string) > 36 and len(string.split(". ")[0]) < 64:
                string = string.split(". ")[0].strip()
            if len(string) > 36 and len(string.split(", ")[0]) < 64:
                string = string.split(", ")[0].strip()
            if len(string) > 36 and len(string.split(" (")[0]) < 64:
                string = string.split(" (")[0].strip()
            if len(string) > 36 and len(string.split("-")[0]) < 64:  # TODO sure?
                string = string.split("-")[0].strip()
            if len(string) > 36 and len(string.split(".")[0]) < 64:
                string = string.split(".")[0].strip()
            if len(string) > 36 and len(string.split(",")[0]) < 64:
                string = string.split(",")[0].strip()
            string = string.replace('"', "'")
            if string.endswith(":"):
                string = string[:-1]
            if len(string) > 58:
                string = field_name.split("_")[-1]

            if string != doc and string != doc[:-1]:
                # help is only useful it adds more than a ponctuation symbol
                doc = wrap_text(doc, 8, 78, initial_indent=14, multi=True)
                help_attr = "help=%s" % (doc)
        if string in unique_labels:
            string = "{} ({})".format(string, field_name)
            if len(string) > 58:
                string = field_name.split("_")[-1]
        unique_labels.add(string)
        return string, help_attr

    @classmethod
    def generate_model_(
        cls,
        wrtmodels,
        unique_name_map,
        options,
        generate_ds,
        implicit_many2ones,
        labels,
        class_skip,
        remapped_simple_types,
        module_name,
    ):

        # we pass the generateDS package as an argument to avoid
        # having to import it dynamically from a custom location
        # multiple times
        mapName = generate_ds.mapName
        cleanupName = generate_ds.cleanupName
        AnyTypeIdentifier = generate_ds.AnyTypeIdentifier

        class_suffixes = options.class_suffixes
        Lib_name = options.schema_name
        # Simplified version: 2 digits only. # TODO make it flexible
        Version = "".join([i for i in options.version if i.isdigit()][:2])
        if class_suffixes:
            model_suffix = "_model"
        else:
            model_suffix = ""

        # TODO via options
        Date_type_table.update({"TData": None})
        DateTime_type_table.update({"TDateTimeUTC": None})
        Boolean_type_table.update({"byte": None})
        Simple_type_table.update(Date_type_table)
        Simple_type_table.update(DateTime_type_table)
        Boolean_type_table.update(DateTime_type_table)
        # wrtmodels("%s" % (Simple_type_table,))

        class_name = unique_name_map.get(cls.__name__)
        odoo_class_name = class_name.replace("Type", "")
        odoo_class = odoo_class_name[0].capitalize() + odoo_class_name[1:100]
        # TODO regexp replace
        #        field_prefix = "%s_%s__" % (Lib_name, odoo_class_name.lower())
        field_prefix = "{}{}_".format(Lib_name, Version)

        wrtmodels(
            "\n\nclass %s%s(models.AbstractModel):\n"
            % (
                odoo_class,
                model_suffix,
            )
        )
        if cls.__doc__:
            wrtmodels("    {}\n".format(wrap_text(cls.__doc__, 4, 79)))
            # setting _description with docstring avoids re-splitting
            # doc lines again once they were formatted for the Python lib
            wrtmodels('    _description = textwrap.dedent("    %s" % (__doc__,))\n')
        else:
            wrtmodels("    _description = '%s'\n" % (odoo_class_name.lower()))
        wrtmodels(
            "    _name = '%s.%s.%s'\n"
            % (
                Lib_name,
                Version,
                odoo_class_name.lower(),
            )
        )
        wrtmodels("    _inherit = 'spec.mixin.{}'\n".format(Lib_name))
        wrtmodels("    _generateds_type = '%s'\n" % (cls.__name__))
        if len(cls.member_data_items_) == 0:
            class_skip.append(cls.__name__)
            return

        if class_name in implicit_many2ones:
            for item in implicit_many2ones[class_name]:
                comodel = item[0].replace("Type", "")
                target_field = item[1]
                wrtmodels(
                    '    %s%s_%s_id = fields.Many2one(\n        "%s.%s.%s")\n'
                    % (
                        field_prefix,
                        target_field,
                        comodel,
                        Lib_name,
                        Version,
                        comodel.lower(),
                    )
                )

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
                """    %schoice%s = fields.Selection(["""
                % (
                    field_prefix,
                    k,
                )
            )  # TODO duplicate name?
            #            for i in v:
            #                wrtmodels("\n        ('%s%s', '%s')," % (field_prefix, i, i))

            items = ",\n        ".join(
                ["('{}{}', '{}')".format(field_prefix, i, i) for i in v]
            )
            wrtmodels("\n        {}".format(items))
            label = "/".join(i for i in v)
            if len(label) > 50:
                label = "%s..." % (label[0:50])
            wrtmodels("""],\n        "%s")\n""" % (label))

        unique_labels = set()
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
            while data_type in Defined_simple_type_table:
                data_type = Defined_simple_type_table[data_type].get_type_name_()
            name = mapName(cleanupName(name))
            field_name = "{}{}".format(field_prefix, name)
            clean_data_type = mapName(cleanupName(data_type))
            if data_type == AnyTypeIdentifier:
                data_type = "string"
            string, help_attr = cls.extract_string_help_select(
                spec.get_name(), spec_doc, unique_labels
            )

            if len(spec.get_data_type_chain()) == 0 or not isinstance(
                spec.get_data_type_chain(), list
            ):
                original_st = data_type
            else:
                original_st = spec.get_data_type_chain()[0]

            if is_optional:
                options = 'string="{}"'.format(string)
            else:
                if len(string) + len(field_name) > 30:
                    options = 'string="{}",\n        xsd_required=True'.format(string)
                else:
                    options = 'string="{}", xsd_required=True'.format(string)

            if choice is not None:
                options = """choice='{}',\n        {}""".format(choice, options)

            options_nohelp = options
            if data_type in Simple_type_table:  # and original_st != 'string':
                options = '{},\n        xsd_type="{}"'.format(options, original_st)

            if help_attr:
                options = "{},\n        {}".format(
                    options,
                    help_attr,
                )
            if data_type in Simple_type_table:
                if "TDec_" in original_st:  # TODO make more flexible
                    digits = int(original_st[8])
                else:
                    digits = False
                if data_type in Integer_type_table:
                    wrtmodels(
                        "    %s = fields.Integer(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif data_type in Float_type_table or digits and digits != MONETARY_DIGITS:
                    if digits:
                        if len(string) > 50:
                            options = "\n        {}".format(options)
                            options = "digits={},{}".format(digits, options)
                        else:
                            options = "digits={}, {}".format(digits, options)
                    wrtmodels(
                        "    %s = fields.Float(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif data_type in Decimal_type_table or "TDec_" in original_st:
                    wrtmodels(
                        "    %s = fields.Monetary(\n        "
                        'currency_field="brl_currency_id",\n        %s)\n'
                        % (field_name, options)
                    )
                elif data_type in Date_type_table or original_st in Date_type_table:
                    wrtmodels(
                        "    %s = fields.Date(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif (
                    data_type in DateTime_type_table
                    or original_st in DateTime_type_table
                ):
                    wrtmodels(
                        "    %s = fields.Datetime(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif data_type in Time_type_table:
                    sys.stderr.write(
                        "Unhandled simple type: %s %s\n"
                        % (
                            field_name,
                            data_type,
                        )
                    )
                    wrtmodels(
                        "    %s = fields.TimeField(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif data_type in Boolean_type_table:
                    wrtmodels(
                        "    %s = fields.Boolean(\n        %s)\n"
                        % (
                            field_name,
                            options,
                        )
                    )
                elif data_type in String_type_table:
                    if (
                        Defined_simple_type_table.get(original_st)
                        and (Defined_simple_type_table[original_st]).get_enumeration_()
                    ):
                        if remapped_simple_types.get(original_st):
                            enum_const = remapped_simple_types[original_st]
                        else:
                            enum_const = original_st
                        enum_type = Defined_simple_type_table[original_st]
                        string, help_attr = cls.extract_string_help_select(
                            field_name,
                            enum_type.get_descr_() or spec_doc,
                            unique_labels,
                        )
                        if help_attr:
                            options = "{},\n        {}".format(
                                options_nohelp, help_attr
                            )
                        wrtmodels(
                            "    %s = fields.Selection(\n        %s,\n        %s)\n"
                            % (
                                field_name,
                                enum_const,
                                options,
                            )
                        )
                    else:
                        #                        if len(string) + len(field_name) > 51:
                        options = "\n        {}".format(options)
                        wrtmodels(
                            "    %s = fields.Char(%s)\n"
                            % (
                                field_name,
                                options,
                            )
                        )  # TODO size
                else:
                    sys.stderr.write(
                        "Unhandled simple type: %s %s\n"
                        % (
                            name,
                            data_type,
                        )
                    )

            elif not Defined_simple_type_table.get(data_type):
                mapped_type = unique_name_map.get(clean_data_type)
                if mapped_type is not None:
                    clean_data_type = mapped_type.replace("Type", "")
                    # TODO regexp replace
                if any(re.search(pattern, clean_data_type) for pattern in class_skip):
                    continue
                if spec.get_container() == 0:  # name in cls._many2one:
                    wrtmodels(
                        '    %s = fields.Many2one(\n        "%s.%s.%s",\n'
                        % (field_name, Lib_name, Version, clean_data_type.lower())
                    )
                    wrtmodels("        %s)\n" % (options))
                    # TODO is ondelete='cascade' really the exception?
                else:
                    wrtmodels(
                        '    %s = fields.One2many(\n        "%s.%s.%s",\n'
                        % (field_name, Lib_name, Version, clean_data_type.lower())
                    )
                    wrtmodels(
                        '        "{}_{}_id",\n'.format(field_name, odoo_class_name)
                    )
                    wrtmodels("        {}\n".format(options))
                    # NOTE can we force at least one unless is_optional?

                    wrtmodels("    )\n")
