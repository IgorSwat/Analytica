from app.data_flow.flow import DataFlow


# A class designed to keep the current state of app and fix frontend view reloads problem
class StateHandler:

    # A configuration of all possible user inputs, that affects any view
    # --- First value is a "default value", which is a special value used to identify initial request
    # --- Second value is a "standard value", which is a typical value passed to processor and used in data processing
    inputs = {
        "selection": ("xxxxx", "1-100"),
        "numeric_method": ("", "standard"),
        "n_components": (0, 2)
    }

    saved_inputs = {}

    def __init__(self, flow: DataFlow):
        self.flow : DataFlow = flow


    # Return state of navbar: whether buttons are disabled or enabled
    def get_navbar_state(self):
        # Define the navbar state connections
        states = {}
        states["nav-data"] = self.flow.get_processor("raw_data") is not None
        states["nav-normalize"] = states["nav-data"]
        states["nav-pca"] = states["nav-data"]
        states["nav-clusters"] = False  # Just for now...

        return states


    # Correct input in case of receiving a special value indicating an initial request
    def correct_input(self, input_value, input_name, node_id):
        if input_name in self.inputs:
            values = self.inputs[input_name]
            if input_value == values[0] and self.flow.load_memory(node_id) is not None:
                return None         # The input was already processes, so we should keep the previous state
            elif input_value == values[0]:
                return values[1]    # We received an initial request, but nothing has been done before in the view
        return input_value  # Either input_name not defined or a received a typical value
