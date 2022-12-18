import re
import json

_supported_types = ["text", "number"]

_available_instructions = {
    "ensure": {
        "args": [
            "ref",
            "any"
        ]
    },
    "expect": {
        "args": [
            "array"
        ]
    },
    "call": {
        "args": [
            "any"
        ]
    },
    "print": {
        "args": [
            "any"
        ]
    }
}

_cache = {
    "context": {},
    "fns": {}
}


def _load_context(context):
    _cache["context"] = context


def _load_fns(fns):
    _cache["fns"] = fns


def _parse_line(line):
    regex = r"(# ?.*|\w+)(\(.*?\))?"

    matches = re.findall(regex, line)

    if len(matches) < 2:
        raise Exception("Missing type and/or label")

    row_type = matches[1][0]

    if row_type not in _supported_types:
        raise Exception("Unsupported type \"{}\"".format(row_type))

    if matches[-1][0][0] == "#":
        matches.pop()

    # transfer object
    t_obj = {
        "label": matches[0][0],
        "type": row_type,
        "raw": matches[2:],
        "instruction_set_list": []  # instruction list divisions
    }

    return t_obj


def _resolve(ref):
    if ref[0] == "~":
        ref = _cache["context"][ref[1:]]

    return ref


def _check_type(c_type, value, prompt=False):
    if c_type == "ref":
        if value[0] != "~":
            raise Exception("\"{}\" must be of type ref".format(value))
    elif c_type == "number":
        # TODO: find general solution for prompt
        try:
            int(value)
        except:
            if prompt:
                while True:
                    try:
                        answer = int(input("\"{}\" must be of type number: ".format(value)))
                        return answer
                    except:
                        print("Invalid answer")
            else:
                raise Exception("\"{}\" must be of type number".format(value))
    elif c_type == "array":
        try:
            if value[0] != "[" or value[-1] != "]":
                raise Exception()

            json.loads(value)
        except:
            raise Exception("\"{}\" must be of type array".format(value))

    # TODO: add types

    return value


def _interpret(t_obj):
    instruction_set_list = []

    # whether a new division should be opened
    is_new_division = True

    for raw_instruction in t_obj["raw"]:
        instruction = raw_instruction[0]
        parameters = raw_instruction[1]
        args = re.findall(r"\((.*)\)", parameters)

        if instruction in ["or"]:
            is_new_division = True
            continue

        # map/split args
        if len(args):
            _args = []
            args = re.split(r'(?=(?:[^\"]|\"(?:[^\"\\]|\\.)*\")*)(?:^|,)(?![^\[]*\])', args[0])
            args.pop(0)
            args = list((map(lambda arg: arg.strip(), args)))
            args = list((map(lambda arg: arg.strip('"'), args)))

        # remove empty string
        if len(args) == 1 and not args[0]:
            args = []

        if instruction not in _available_instructions:
            raise Exception("Unknown command \"{}\"".format(instruction))

        command_definition = _available_instructions[instruction]
        command_args = command_definition["args"]

        if len(command_args) != len(args):
            raise Exception("Invalid number of arguments for instruction " + instruction)

        for i, arg_type in enumerate(command_args):
            _check_type(arg_type, args[i])

        if is_new_division:
            is_new_division = False
            instruction_set_list.append([])

        instruction_set_list[-1].append({
            "name": instruction,
            "args": args,
        })

    t_obj["instruction_set_list"] = instruction_set_list

    return t_obj


def _execute(value, t_obj):
    # check type of value
    value = _check_type(t_obj["type"], value, True)

    # add value to cache
    _cache["context"][t_obj["label"]] = value

    results = []

    for instruction_set in t_obj["instruction_set_list"]:
        # current value
        c_val = value

        for instruction in instruction_set:
            instruction_name = instruction["name"]
            arg_types = _available_instructions[instruction_name]["args"]
            resolved_args = []

            for i, arg in enumerate(instruction["args"]):
                arg_type = arg_types[i]

                if arg_type == "number":
                    arg = int(arg)
                if arg_type == "ref":
                    try:
                        arg = _cache["context"][arg[1:]]
                    except:
                        raise Exception("Could not resolve ref \"{}\"".format(arg))
                if arg_type == "array":
                    arg = json.loads(arg)
                if arg_type == "any":
                    # could be ref
                    arg = _resolve(arg)

                # TODO: add more types

                resolved_args.append(arg)

            if instruction_name == "ensure":
                if resolved_args[0] != resolved_args[1]:
                    c_val = ""
                    break

            elif instruction_name == "expect":
                if c_val not in resolved_args[0]:
                    if len(resolved_args[0]) == 1:
                        c_val = resolved_args[0][0]
                    else:
                        print("----------")
                        print("[-2]: Delete entry")
                        print("[-1]: Delete value")

                        for i, answer in enumerate(resolved_args[0]):
                            print("[" + str(i) + "]: " + answer)

                        while True:
                            try:
                                answer_index = int(input("Please help me understand \"{}\": ".format(c_val)))

                                if answer_index == -2:
                                    return False

                                if answer_index == -1:
                                    c_val = ""
                                    break

                                c_val = resolved_args[0][answer_index]
                                break
                            except:
                                print("Invalid answer")

            elif instruction_name == "print":
                print("PRINT {}".format(resolved_args[0]))

            elif instruction_name == "call":
                if resolved_args[0] not in _cache["fns"]:
                    raise Exception("Function \"{}\" for call execution was not found".format(resolved_args[0]))

                c_val = _cache["fns"][resolved_args[0]](value)

        results.append(c_val)

    for result in results:
        if result:
            return result

    result = "" if results else value

    return result


def validate(csv_file, asd_file, fns=None):
    entries = []
    memory = []
    valid_entries = []

    if fns:
        _load_fns(fns)

    with open(csv_file, encoding="utf8") as cf:
        for index, entry in enumerate(cf.readlines()):
            entry = entry.strip("\n")

            entry_data = re.split(r',(?=(?:[^"]|"[^"]*")*$)', entry)
            entries.append(entry_data)

    with open(asd_file, encoding="utf8") as af:
        for i, md in enumerate(af.readlines()):
            try:
                ds = _parse_line(md)
            except Exception as e:
                print("An error occurred while parsing line {}: {}".format(str(i), str(e)))
                return

            try:
                ds = _interpret(ds)
            except Exception as e:
                print("An error occurred while interpreting line {}: {}".format(str(i), str(e)))
                return

            memory.append(ds)

    for entry in list(entries[1:]):
        for i, md in enumerate(memory):
            try:
                print("----------")
                print("Checking: \"{}\"".format(entries[0][i]))
                result = _execute(entry[i], md)
            except Exception as e:
                print("An error occurred while executing line {}: {}".format(str(i), str(e)))
                return

            entry[i] = result

            if result != "" and not result:
                break
        else:
            valid_entries.append(entry)

    '''
    for i, md in enumerate(memory):
        for entry in list(entries[1:]):
            entry_dict = {}

            for j, field in enumerate(entry):
                entry_dict[entries[0][j]] = field

            _load_context(entry_dict)

            try:
                print("----------")
                print("Checking: \"{}\"".format(entries[0][i]))
                result = _execute(entry[i], md)
            except Exception as e:
                print("An error occurred while executing line {}: {}".format(str(i), str(e)))
                return

            entry[i] = result

            if result != "" and not result:
                break
        else:
            valid_entries.append(entry)
    '''

    return valid_entries
