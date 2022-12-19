import re
from astav import supported_types


def parse_line(line):
    regex = r"(# ?.*|\w+|\|+)(\(.*?\))?"

    matches = re.findall(regex, line)

    # don't parse comment lines
    if len(matches) == 1 and matches[0][0][0] == "#":
        return None

    if len(matches) < 2:
        raise Exception("Missing type and/or label")

    row_type = matches[1][0]

    if row_type not in supported_types:
        raise Exception("Unsupported type \"{}\"".format(row_type))

    if matches[-1][0][0] == "#":
        matches.pop()

    # transfer object
    t_obj = {
        "label": matches[0][0],
        "type": row_type,
        "raw": matches[2:],
        "instruction_set_list": []
    }

    return t_obj