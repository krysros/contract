import argparse
import yaml
import os

from docxtpl.template import DocxTemplate, TemplateError
from jinja2 import Environment
from babel.numbers import format_currency
from babel.dates import (
    format_date,
    format_datetime,
)
from slownie import slownie_zl100gr

TEMPLATE_ARG = "template_path"
YAML_ARG = "yaml_path"
OUTPUT_ARG = "output_filename"
OVERWRITE_ARG = "overwrite"
QUIET_ARG = "quiet"


def make_arg_parser():
    parser = argparse.ArgumentParser(
        usage=f"python -m docxtpl [-h] [-o] [-q] {TEMPLATE_ARG} {YAML_ARG} {OUTPUT_ARG}",
        description="Make docx file from existing template docx and yaml data.",
    )
    parser.add_argument(
        TEMPLATE_ARG, type=str, help="The path to the template docx file."
    )
    parser.add_argument(
        YAML_ARG, type=str, help="The path to the yaml file with the data."
    )
    parser.add_argument(
        OUTPUT_ARG, type=str, help="The filename to save the generated docx."
    )
    parser.add_argument(
        "-" + OVERWRITE_ARG[0],
        "--" + OVERWRITE_ARG,
        action="store_true",
        help="If output file already exists, overwrites without asking for confirmation",
    )
    parser.add_argument(
        "-" + QUIET_ARG[0],
        "--" + QUIET_ARG,
        action="store_true",
        help="Do not display unnecessary messages",
    )
    return parser


def get_args(parser):
    try:
        parsed_args = vars(parser.parse_args())
        return parsed_args
    # Argument errors raise a SystemExit with code 2. Normal usage of the
    # --help or -h flag raises a SystemExit with code 0.
    except SystemExit as e:
        if e.code == 0:
            raise SystemExit
        else:
            raise RuntimeError(f"Correct usage is:\n{parser.usage}")


def is_argument_valid(arg_name, arg_value, overwrite):
    # Basic checks for the arguments
    if arg_name == TEMPLATE_ARG:
        return os.path.isfile(arg_value) and arg_value.endswith(".docx")
    elif arg_name == YAML_ARG:
        return os.path.isfile(arg_value) and (
            arg_value.endswith(".yml") or arg_value.endswith(".yaml")
        )
    elif arg_name == OUTPUT_ARG:
        return arg_value.endswith(".docx") and check_exists_ask_overwrite(
            arg_value, overwrite
        )
    elif arg_name in [OVERWRITE_ARG, QUIET_ARG]:
        return arg_value in [True, False]


def check_exists_ask_overwrite(arg_value, overwrite):
    # If output file does not exist or command was run with overwrite option,
    # returns True, else asks for overwrite confirmation. If overwrite is
    # confirmed returns True, else raises OSError.
    if os.path.exists(arg_value) and not overwrite:
        try:
            msg = f"File {arg_value} already exists, would you like to overwrite the existing file? (y/n) "
            if input(msg).lower() == "y":
                return True
            else:
                raise OSError
        except OSError:
            raise RuntimeError(
                "File {arg_value} already exists, please choose a different name."
            )
    else:
        return True


def validate_all_args(parsed_args):
    overwrite = parsed_args[OVERWRITE_ARG]
    # Raises AssertionError if any of the arguments is not validated
    try:
        for arg_name, arg_value in parsed_args.items():
            if not is_argument_valid(arg_name, arg_value, overwrite):
                raise AssertionError
    except AssertionError:
        raise RuntimeError(f'The specified {arg_name} "{arg_value}" is not valid.')


def get_yaml_data(yaml_path):
    with open(yaml_path, encoding="utf-8") as file:
        try:
            document = file.read()
            yaml_data = yaml.load(document, Loader=yaml.CLoader)
            return yaml_data
        except yaml.YAMLError as e:
            if hasattr(e, "problem_mark"):
                mark = e.problem_mark
                line = mark.line + 1
                column = mark.column + 1
                print(
                    f"There was an error on line {line}, column {column} while trying to parse file {yaml_path}"
                )
            raise RuntimeError("Failed to get yaml data.")


def make_docxtemplate(template_path):
    try:
        return DocxTemplate(template_path)
    except TemplateError:
        raise RuntimeError("Could not create docx template.")


def render_docx(doc, yaml_data, jinja_env):
    try:
        doc.render(yaml_data, jinja_env)
        return doc
    except TemplateError:
        raise RuntimeError("An error ocurred while trying to render the docx")


def save_file(doc, parsed_args):
    try:
        output_path = parsed_args[OUTPUT_ARG]
        doc.save(output_path)
        if not parsed_args[QUIET_ARG]:
            print(f"Document successfully generated and saved at {output_path}")
    except OSError as e:
        print(f"{e.strerror}. Could not save file {e.filename}.")
        raise RuntimeError("Failed to save file.")


def fmt_datetime(dt):
    return format_datetime(dt, format="dd.MM.YYYY", locale="pl_PL")


def fmt_date(d):
    return format_date(d, format="long", locale="pl_PL")


def fmt_currency(c):
    return format_currency(c, "PLN", locale="pl_PL")


def in_words(v):
    return slownie_zl100gr(v)


def make_jinja_environment():
    environment = Environment()
    environment.filters["fmt_datetime"] = fmt_datetime
    environment.filters["fmt_date"] = fmt_date
    environment.filters["fmt_currency"] = fmt_currency
    environment.filters["in_words"] = in_words
    return environment


def main():
    parser = make_arg_parser()
    # Everything is in a try-except block that catches a RuntimeError that is
    # raised if any of the individual functions called cause an error
    # themselves, terminating the main function.
    parsed_args = get_args(parser)
    try:
        validate_all_args(parsed_args)
        yaml_data = get_yaml_data(os.path.abspath(parsed_args[YAML_ARG]))
        doc = make_docxtemplate(os.path.abspath(parsed_args[TEMPLATE_ARG]))
        jinja_env = make_jinja_environment()
        doc = render_docx(doc, yaml_data, jinja_env)
        save_file(doc, parsed_args)
    except RuntimeError as e:
        print("Error: " + e.__str__())
        return
    finally:
        if not parsed_args[QUIET_ARG]:
            print("Exiting program!")


if __name__ == "__main__":
    main()
