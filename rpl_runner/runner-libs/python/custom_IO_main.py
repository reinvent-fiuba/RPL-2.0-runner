# First overwrite the 'input' function so that we print what we get as we would see in a terminal
import builtins

_input = input


def my_input(arg=""):
    a = _input(arg)
    print(a)
    return a


builtins.input = my_input


# Run the student code
import assignment_main
