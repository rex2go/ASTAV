import json
from astav import check_type, cache, available_instructions, resolve


def execute(value, t_obj):
    # check type of value
    value = check_type(t_obj["type"], value, True)

    if value != 0 and value != '' and not value:
        return False

    # add value to cache
    cache["context"][t_obj["label"]] = value

    results = []

    for instruction_set in t_obj["instruction_set_list"]:
        # current value
        c_val = value

        for instruction in instruction_set:
            instruction_name = instruction["name"]
            arg_types = available_instructions[instruction_name]["args"]
            resolved_args = []

            for i, arg in enumerate(instruction["args"]):
                arg_type = arg_types[i]

                if arg_type == "number":
                    arg = int(arg)
                if arg_type == "ref":
                    try:
                        arg = cache["context"][arg[1:]]
                    except:
                        raise Exception("Could not resolve ref \"{}\"".format(arg))
                if arg_type == "array":
                    arg = json.loads(arg)
                if arg_type == "any":
                    # could be ref
                    arg = resolve(arg)

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
                if resolved_args[0] not in cache["fns"]:
                    raise Exception("Function \"{}\" for call execution was not found".format(resolved_args[0]))

                c_val = cache["fns"][resolved_args[0]](c_val)

        results.append(c_val)

    for result in results:
        if result:
            return result

    result = "" if results else value

    return result