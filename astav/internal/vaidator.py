import re
from astav import load_fns, parse_line, interpret, load_context, execute


def validate(csv_file, asd_file, fns=None):
    entries = []
    memory = []
    valid_entries = []

    if fns:
        load_fns(fns)

    with open(csv_file, encoding="utf8") as cf:
        for index, entry in enumerate(cf.readlines()):
            entry = entry.strip("\n")

            entry_data = re.split(r',(?=(?:[^"]|"[^"]*")*$)', entry)
            entries.append(entry_data)
            valid_entries.append(entry_data)

    with open(asd_file, encoding="utf8") as af:
        for i, md in enumerate(af.readlines()):
            try:
                ds = parse_line(md)

                if ds is None:
                    continue
            except Exception as e:
                print("An error occurred while parsing line {}: {}".format(str(i), str(e)))
                return

            try:
                ds = interpret(ds)
            except Exception as e:
                print("An error occurred while interpreting line {}: {}".format(str(i), str(e)))
                return

            ds["index"] = i

            memory.append(ds)

    row_md_cache = []

    for row_md in memory:
        row_md_cache.append(row_md)
        i = row_md["index"]

        for entry in list(entries[1:]):
            if entry not in valid_entries:
                continue

            stripped_entry = list((map(lambda arg: str(arg).strip('"'), entry)))

            entry_dict = {}

            for j, field in enumerate(stripped_entry):
                if len(row_md_cache) <= j:
                    break

                entry_dict[row_md_cache[j]["label"]] = field

            load_context(entry_dict)

            try:
                print("----------")
                print("Checking: \"{}\"".format(entries[0][i]))
                result = execute(stripped_entry[i], row_md)
            except Exception as e:
                print("An error occurred while executing line {}: {}".format(str(i), str(e)))
                return

            entry[i] = result

            if result != "" and not result:
                valid_entries.remove(entry)

    return valid_entries