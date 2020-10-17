#!/usr/bin/env python

"""
Synopsis:
    Generate Odoo models.py from XML schema.
Usage:
    python gends_run_gen_odoo.py [options] <schema_file>
Options:
    -h, --help      Display this help message.
    -f, --force     Overwrite the following files without asking:
                        <schema>lib.py
                        generateds_definedsimpletypes.py
                        models.py
    -p, --path-to-generateDS-script=/path/to/generateDS.py
                    Path to the generateDS.py script.
    -v, --verbose   Display additional information while running.
    -s, --script    Write out (display) the command lines used.  Can
                    be captured and used in a shell script, for example.
    --no-class-suffixes
                    Do not add suffix "_model" and _form" to
                    generated class names.
    -d, --directory Output directory
Examples:
    python gends_run_gen_odoo.py my_schema.xsd
    python gends_run_gen_odoo.py -f -p ../generateDS.py my_other_schema.xsd

"""

import getopt
import os
import sys
from glob import glob
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen

ODOO_GEN_HOME = os.environ.get("ODOO_GEN_HOME", str(Path(__file__).parent))


def generate(options, schema_file_name):
    schema_name_stem = os.path.splitext(os.path.split(schema_file_name)[1])[0]
    # NOTE: a file like name.v4.xsd with double dot won't generate a valid .py
    schema_name_stem = schema_name_stem.replace(".", "")
    bindings_file_name = "{}lib.py".format(schema_name_stem)
    bindings_file_stem = os.path.splitext(bindings_file_name)[0]
    model_file_name = "models.py"
    dbg_msg(options, "schema_name_stem: {}\n".format(schema_name_stem))
    dbg_msg(options, "bindings_file_name: {}\n".format(bindings_file_name))
    if options["force"]:
        file_names = (
            glob(bindings_file_name)
            + glob("%s.pyc" % bindings_file_stem)
            + glob("__pycache__/%s.*.pyc" % bindings_file_stem)
        )
        for file_name in file_names:
            dbg_msg(options, "removing: %s\n" % file_name)
            os.remove(file_name)
    else:
        flag1 = exists(bindings_file_name)
        flag2 = exists(model_file_name)
        if flag1 or flag2:
            return
    args = (
        "python3",
        options["path"],
        "-f",
        "-o",
        "{}/{}".format(options["output_dir"], bindings_file_name),
        "--member-specs=list",
        schema_file_name,
    )
    if not run_cmd(options, args):
        print("error")
        return
    args = (
        "{}/gends_extract_simple_types.py".format(ODOO_GEN_HOME),
        "-f",
        "-p",
        options["path"].replace("/generateDS.py", ""),  # TODO does it work?
        "-o",
        "{}/{}".format(options["output_dir"], "generateds_definedsimpletypes.py"),
        schema_file_name,
    )
    if not run_cmd(options, args):
        print("error")
        return
    if options["class_suffixes"]:
        args = (
            "python3",
            "%s/gends_generate_odoo.py" % (ODOO_GEN_HOME),
            "-f",
            "-p",
            options["path"].replace("/generateDS.py", ""),  # TODO does it work
            "-l",
            options["schema_name"],
            "-x",
            options["version"],
            "-d",
            options["output_dir"],
            "-n",
            options["notes"],
            "-e",
            options["skip"],
            "-s",
            schema_file_name,
            bindings_file_stem,
        )
    else:
        args = (
            "python3",
            "%s/gends_generate_odoo.py" % (ODOO_GEN_HOME),
            "-f",
            "-p",
            options["path"].replace("/generateDS.py", ""),  # TODO does it work
            "-l",
            options["schema_name"],
            "-x",
            options["version"],
            "-d",
            options["output_dir"],
            "-n",
            options["notes"],
            "-e",
            options["skip"],
            "--no-class-suffixes",
            "-s",
            schema_file_name,
            bindings_file_stem,
        )
    if not run_cmd(options, args):
        print("error")
        return


def run_cmd(options, args):
    msg = "{}\n".format(" ".join(args))
    dbg_msg(options, "*** running {}".format(msg))
    if options.get("script"):
        write_msg(options, msg)
    process = Popen(args, stderr=PIPE, stdout=PIPE)
    content1 = process.stderr.read()
    content2 = process.stdout.read()
    if content1:
        sys.stderr.write("*** error ***\n")
        sys.stderr.write(content1.decode("utf-8"))
        sys.stderr.write("*** error ***\n")
    if content2:
        dbg_msg(options, "*** message ***\n")
        dbg_msg(options, content2.decode("utf-8"))
        dbg_msg(options, "*** message ***\n")
    return True


def exists(file_name):
    if os.path.exists(file_name):
        msg = "File {} exists.  Use -f/--force to overwrite.\n".format(file_name)
        sys.stderr.write(msg)
        return True
    return False


def dbg_msg(options, msg):
    if options["verbose"]:
        if isinstance(msg, str):
            sys.stdout.write(msg)
        else:
            sys.stdout.write(msg.decode("utf-8"))


def write_msg(options, msg):
    if isinstance(msg, str):
        sys.stdout.write(msg)
    else:
        sys.stdout.write(msg.decode("utf-8"))


def usage():
    sys.exit(__doc__)


def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            args,
            "hvfp:l:x:d:s:n:e:",
            [
                "help",
                "verbose",
                "script",
                "force",
                "path-to-generateDS-script=",
                "schema_name",
                "version",
                "directory=",
                "no-class-suffixes",
                "notes",
                "skip",
            ],
        )
    except:
        usage()
    options = {}
    options["force"] = False
    options["verbose"] = False
    options["script"] = False
    options["path"] = "./generateDS.py"
    options["class_suffixes"] = True
    options["notes"] = ""
    options["skip"] = ""
    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-f", "--force"):
            options["force"] = True
        elif opt in ("-v", "--verbose"):
            options["verbose"] = True
        elif opt in ("-s", "--script"):
            options["script"] = True
        elif opt in ("-p", "--path-to-generateDS-script"):
            options["path"] = val
        elif opt == "--no-class-suffixes":
            options["class_suffixes"] = False
        elif opt in ("-d", "--directory"):
            options["output_dir"] = val
        elif opt in ("-l", "--schema_name"):
            options["schema_name"] = val
        elif opt in ("-x", "--version"):
            options["version"] = val
        elif opt in ("-n", "--notes"):
            options["notes"] = val
        elif opt in ("-e", "--skip"):
            options["skip"] = val
    if not os.path.exists(options["path"]):
        if not which("generateDS"):
            sys.exit(
                "\n*** error: Cannot find generateDS.py.  "
                'Install generateDS or use "-p path" command line option.\n'
            )
        else:
            options["path"] = "{}.py".format(str(which("generateDS")))
    if len(args) != 1:
        usage()
    schema_name = args[0]
    generate(options, schema_name)


if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    # import ipdb; ipdb.set_trace()
    main()
