import re
from astav import available_instructions, check_type


def interpret(t_obj):
    instruction_set_list = []

    # whether a new division should be opened
    is_new_division = True

    for raw_instruction in t_obj["raw"]:
        instruction = raw_instruction[0]
        parameters = raw_instruction[1]
        args = re.findall(r"\((.*)\)", parameters)

        if instruction in ["or", "|", "||"]:
            is_new_division = True
            continue

        # map/split args
        if len(args):
            _args = []
            # split comma (except for strings and arrays)
            args = re.split(r'(?=(?:[^\"]|\"(?:[^\"\\]|\\.)*\")*)(?:^|,)(?![^\[]*\])', args[0])
            # first arg is always empty
            args.pop(0)
            args = list((map(lambda arg: arg.strip(), args)))
            args = list((map(lambda arg: arg.strip('"'), args)))

        # remove empty string
        if len(args) == 1 and not args[0]:
            args = []

        if instruction not in available_instructions:
            raise Exception("Unknown command \"{}\"".format(instruction))

        instruction_definition = available_instructions[instruction]
        instruction_args = instruction_definition["args"]

        if len(instruction_args) != len(args):
            raise Exception("Invalid number of arguments for instruction " + instruction)

        for i, arg_type in enumerate(instruction_args):
            check_type(arg_type, args[i])

        if is_new_division:
            is_new_division = False
            instruction_set_list.append([])

        instruction_set_list[-1].append({
            "name": instruction,
            "args": args,
        })

    t_obj["instruction_set_list"] = instruction_set_list

    return t_obj