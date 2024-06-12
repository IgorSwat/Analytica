# Base class for all types of processors, to not forget about error logic :)
class Processor:

    def __init__(self):
        self.error = None


    def set_error(self, error):
        self.error = error
        return None


    def extract_arg(self, input, arg_name, arg_type):
        if arg_name not in input:
            return self.set_error(f"'{arg_name}' argument not provided")
        arg = input[arg_name]
        if not isinstance(arg, arg_type):
            return self.set_error(f"'Incorrect type of {arg_name}' argument")

        return arg