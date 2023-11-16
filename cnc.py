from opcua import ua, Server
import inquirer
import time
import numpy as np
import random

# Create server
server = Server()
server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

# Register namespace
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# Get Objects node
objects = server.get_objects_node()

# Define CNC machine states and spindle control statuses
cnc_states = ["READY", "STOPPED", "ACTIVE", "INTERRUPTED"]
spindle_statuses = ["ACTIVE", "IDLE", "OFF", "FAULT"]
s3_states = [True, False]
MachineStates = [True, False]
Recipes = ["Gear","Shaft","Bolt"]

# Create variables
myvars = {
    "c1": objects.add_variable(idx, "c1", 0.0),  # Continuous variable
    "c2": objects.add_variable(idx, "c2", 0.0),  # Continuous variable
    "c3": objects.add_variable(idx, "c3", 0.0),  # Continuous variable
    "spindle": objects.add_variable(idx, "spindle", "OFF"),  # Spindle control status variable
    "execution": objects.add_variable(idx, "execution", "STOPPED"),  # State variable (CNC Machine State)
    "s3": objects.add_variable(idx, "s3", False),  # State variable (True/False)
    "MachineState": objects.add_variable(idx, "MachineState", False),  # State variable (True/False)
    "Recipe": objects.add_variable(idx, "Recipe", "Gear"),  # Products

}

# Start server
server.start()

try:
    while True:
        variable_question = [
            inquirer.List('variable',
                          message="Which variable do you want to update?",
                          choices=["c1", "c2", "c3", "spindle", "execution", "s3", "MachineState", "Recipe"],
                          ),
        ]

        variable_answer = inquirer.prompt(variable_question)
        selected_variable = variable_answer['variable']

        if selected_variable in ["spindle", "execution", "s3", "MachineState", "Recipe"]:
            # For state variables, ask for a CNC machine state or spindle control status or s3 state
            choices = {
                "spindle": spindle_statuses,
                "execution": cnc_states,
                "s3": s3_states,
                "MachineState": MachineStates,
                "Recipe": Recipes
            }
            current_val = myvars[selected_variable].get_value()
            print(f"\n• Current value for {selected_variable} is '{current_val}'\n")
            value_question = [
                inquirer.List('value',
                              message="Choose a new value for the state variable",
                              choices=choices[selected_variable],
                              ),
                inquirer.Confirm('limited_time',
                                 message='Do you want to set the value for a limited time?',
                                 default=True),
            ]

            value_answer = inquirer.prompt(value_question)
            new_value = value_answer['value']
            if value_answer['limited_time']:
                set_time_question = [
                    inquirer.Text('set_time', message='Enter how long to set the value (in seconds)'),
                ]
                set_time_answer = inquirer.prompt(set_time_question)
                sleep_duration = float(set_time_answer['set_time'])
                print(f"• Value for {selected_variable} is set to '{new_value}' for {sleep_duration} seconds")
                myvars[selected_variable].set_value(new_value)
                time.sleep(sleep_duration)
                myvars[selected_variable].set_value(current_val)
                print(f"• Value for {selected_variable} is changed back to '{current_val}'\n")
            else:
                myvars[selected_variable].set_value(new_value)
                print(f"\n• Value for {selected_variable} is changed to '{new_value}'\n")


        else:
            # For continuous variables, ask for a single value or a range of values
            value_type_question = [
                inquirer.List('value_type',
                              message="Do you want to enter a single value or a range of values?",
                              choices=["Single Value", "Range of Values"],
                              ),
            ]

            value_type_answer = inquirer.prompt(value_type_question)
            value_type = value_type_answer['value_type']

            if value_type == "Single Value":
                value_question = [
                    inquirer.Text('value', message="Enter a new value for the continuous variable"),
                ]
                value_answer = inquirer.prompt(value_question)
                new_value = float(value_answer['value'])
                myvars[selected_variable].set_value(new_value)

            else:  # value_type == "Range of Values"
                range_question = [
                    inquirer.Text('start', message="Enter the start of the range"),
                    inquirer.Text('stop', message="Enter the end of the range"),
                    inquirer.Text('step', message="Enter the step size"),
                    inquirer.Text('sleep_time', message="Enter the sleep time between each value (in seconds)"),
                    inquirer.Confirm('random_order', message="Do you want the values in random order?"),
                ]
                range_answer = inquirer.prompt(range_question)
                start = float(range_answer['start'])
                stop = float(range_answer['stop'])
                step = float(range_answer['step'])
                random_order = range_answer['random_order']
                sleep_time = float(range_answer['sleep_time'])
                values = np.arange(start, stop, step)
                if random_order:
                    np.random.shuffle(values)
                else:
                    values.sort()

                for value in values:
                    myvars[selected_variable].set_value(value)
                    time.sleep(sleep_time)

finally:
    server.stop()
