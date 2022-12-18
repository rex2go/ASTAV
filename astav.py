import re
import json

_supported_types = ["text", "number"]

_available_commands = {
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
}

_context = {
    "data": {}
}


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
        "raw_instructions": matches[2:],
        "instructions": []
    }

    return t_obj


def _resolve(ref):
    if ref[0] == "~":
        ref = _context["data"][ref[1:]]

    return ref


def _check_type(c_type, value, prompt=False):
    if c_type == "ref":
        if value[0] != "~":
            raise Exception("\"{}\" must be of type ref".format(value))
    elif c_type == "number":
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
    instructions = []
    new_instruction = True

    for instruction in t_obj["raw_instructions"]:
        command = instruction[0]
        parameters = instruction[1]
        args = re.findall(r"\((.*)\)", parameters)

        if command in "or":
            new_instruction = True
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

        if command not in _available_commands:
            raise Exception("Unknown command \"{}\"".format(command))

        command_definition = _available_commands[command]
        command_args = command_definition["args"]

        if len(command_args) != len(args):
            raise Exception("Invalid number of arguments for command " + command)

        for i, arg_type in enumerate(command_args):
            _check_type(arg_type, args[i])

        if new_instruction:
            new_instruction = False
            instructions.append([])

        instructions[-1].append({
            "command": command,
            "args": args,
        })

    t_obj["instructions"] = instructions

    return t_obj


def _execute(value, cmd_data):
    value = _check_type(cmd_data["type"], value, True)
    _context["data"][cmd_data["label"]] = value

    group_results = []

    for instruction_group in cmd_data["instructions"]:
        group_result = value

        for instruction in instruction_group:
            command = instruction["command"]
            arg_types = _available_commands[command]["args"]
            resolved_args = []

            for i, arg in enumerate(instruction["args"]):
                arg_type = arg_types[i]

                if arg_type == "number":
                    arg = int(arg)
                if arg_type == "ref":
                    try:
                        arg = _context["data"][arg[1:]]
                    except:
                        raise Exception("Could not resolve ref \"{}\"".format(arg))
                if arg_type == "array":
                    arg = json.loads(arg)

                # TODO: add more types

                resolved_args.append(arg)

            if command == "ensure":
                if resolved_args[0] != resolved_args[1]:
                    group_result = ""
                    break
            elif command == "expect":
                if value not in resolved_args[0]:
                    if len(resolved_args[0]) == 1:
                        group_result = resolved_args[0][0]
                    else:
                        print("[-2]: Delete entry")
                        print("[-1]: Delete value")

                        for i, answer in enumerate(resolved_args[0]):
                            print("[" + str(i) + "]: " + answer)

                        while True:
                            try:
                                answer_index = int(input("Please help me understand \"{}\": ".format(value)))

                                if answer_index == -2:
                                    return False

                                if answer_index == -1:
                                    group_result = ""
                                    break

                                group_result = resolved_args[0][answer_index]
                                break
                            except:
                                print("Invalid answer")

        group_results.append(group_result)

    for group_result in group_results:
        if group_result:
            return group_result

    return "" if group_results else value


def validate(csv_file, asd_file):
    entries = []
    memory = []
    valid_entries = []

    with open(csv_file, encoding="utf8") as cf:
        for index, entry in enumerate(cf.readlines()):
            entry = entry.strip("\n")

            if index == 0:
                entries.append(entry)
                continue

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
                result = _execute(entry[i], md)
            except Exception as e:
                print("An error occurred while executing line {}: {}".format(str(i), str(e)))
                return

            entry[i] = result

            if result != "" and not result:
                break
        else:
            valid_entries.append(entry)

    return valid_entries


print(validate('test.csv', 'test.asd'))
