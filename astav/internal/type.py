import json


def check_type(c_type, value, prompt=False):
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
                        print("----------")
                        print("[-2]: Delete entry")
                        print("[-1]: Delete value")
                        answer = int(input("\"{}\" must be of type number: ".format(value)))

                        if answer == -2:
                            return False

                        if answer == -1:
                            return ''

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
