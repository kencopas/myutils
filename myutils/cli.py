import re
from datetime import datetime
from getpass import getpass


def valid_date(format: str, user_input: str):
    """
    Validates a date input with tokens separated by a '-'
    """

    try:
        # Extract the values from the date and cast each to an int
        values = user_input.split('-')

        # Extract keys from the format (ex: mm-dd-yyyy)
        keys = format.split('-')

        # Map each key to the token value
        tokens = {k: int(v) for k, v in zip(keys, values)}

        year = tokens['yyyy']
        month = tokens.get('mm', 1)
        day = tokens.get('dd', 1)

        # Attempt to convert the date to a datetime and validate year
        datetime(year, month, day)
        return year <= 2025

    except Exception:
        return False


class CLIComponent:
    """Base class for all CLI components.

    This class allows CLI components to be nested and configured using
    keyword arguments and optional child components.

    Args:
        *components (object): Any number of child CLIComponent objects.
        **props (any): Optional properties to store as metadata.
    """

    def __init__(self, *components: object, **props: any) -> None:
        self.components = components
        self.props = props

    @staticmethod
    def enumchoices(text: str, options: dict[str]) -> any:
        """Prompt the user to select from enumerated options.

        Args:
            text (str): The prompt message to display to the user.
            options (dict[str]): A dictionary of options {option_name: option}.

        Returns:
            any: The selected value corresponding to the chosen key.
        """
        # Format the multiple choice options
        keys, enum_options = [], ""

        for index, option in enumerate(options.keys()):
            keys.append((index, option))
            enum_options += f"{index}: {option}\n"

        keys = dict(keys)

        ans = input(f"{text}\n{enum_options}\n")

        # Prompt the user until the input is valid
        while not ans.isdigit() or not (0 <= int(ans) < len(options)):
            ans = input(f"Please choose a valid option:\n{enum_options}")

        return options[keys[int(ans)]]

    @staticmethod
    def prompt_user(text: str, constraints: dict, private: bool = False) -> str:

        """Prompt the user for input and validate against constraints.

        Args:
            text (str): Prompt text to display to the user.
            constraints (dict): Dictionary of constraints to validate input.
            Supported keys include:
                - 'type': a callable that validates/casts the input type
                - 'length': int or list of valid lengths
                - 'value': list or range of valid integer values
                - 'regex': regex string/pattern to fullmatch input
                - 'date': date format for validation (ex: mm-dd-yyyy)
                - 'custom': custom validation function returning bool

        Returns:
            str: Validated user input as a string.
        """

        # Prompt with getpass if private otherwise use input
        prompter = getpass if private else input

        ans = prompter(f"{text}\n")

        # Prompt the user until input is valid
        while True:

            # Test each constraint specified
            for test, value in constraints.items():
                try:
                    match test:
                        # Ensures the input is of the type specified
                        case "type":
                            value(ans)
                        # Ensures input is of the length specified
                        case "length":
                            if type(value) is int:
                                value = [value]
                            if len(ans) not in value:
                                break
                        # Ensures the value is within the range specified
                        case "value":
                            if int(ans) not in value:
                                break
                        # Ensures the value matches a regex pattern
                        case "regex":
                            if not re.fullmatch(value, ans):
                                break
                        # Validates a date of a given format
                        case "date":
                            if not valid_date(value, ans):
                                break
                        # Pass the input through a custom validation function
                        case "custom":
                            if not value(ans):
                                break
                        case _:
                            continue
                except Exception:
                    break
            else:
                break

            ans = prompter(f"\nInvalid Input.\n\n{text}\n")

        return ans

    def run(self) -> dict[str, any]:
        """Stub method for running the CLIComponent.

        Returns:
            dict[str, any]: Output from component (overridden in subclasses).
        """
        pass

# ---------------------------------------------------------------------------------------------------------------------


class MenuDivider(CLIComponent):
    """CLIComponent that runs multiple child components and aggregates outputs.

    Args:
        *components (CLIComponent): CLIComponent instances to be executed.
        id (str): Identifier for this MenuDivider component.
        pass_values (callable, optional): Function that is passed the outputs.
    """

    def __init__(self, *components, id: str, pass_values: callable = None):
        self.components = components
        self.id = id
        self.pass_values = pass_values

    def run(self) -> tuple[str, any]:
        """Runs all child components and collects their outputs.

        Returns:
            dict[str, any]: Dictionary mapping the component's ID to outputs.
        """

        # Construct a selections dictionary by extending each subcomponent's
        selections = {}
        for ui in self.components:
            output = ui.run()
            if type(output) is tuple:
                output = {output[0]: output[1]}
            selections.update(output)

        # Format the output as (id, selections_dict) if there is an id
        output = (self.id, selections)

        # Pass the output to the pass_values function if it exists
        if self.pass_values:
            self.pass_values(output[1])

        return output

# ---------------------------------------------------------------------------------------------------------------------


class MultipleChoice(CLIComponent):
    """A CLIComponent for presenting a multiple-choice selection to the user.

    Args:
        root (bool, optional): If True, loops the prompt upon traversal.
        id (str): Identifier for this component.
        prompt (str): Text to show the user as a prompt.
        options (dict): Mapping of string options to specified component/value.
        pass_values (callable, optional): Function that is passed the outputs.
    """

    def __init__(
        self,
        *,
        root: bool = False,
        id: str,
        prompt: str,
        options: dict,
        pass_values: callable = None
    ):
        self.root = root
        self.id = id
        self.prompt = prompt
        self.options = options
        self.pass_values = pass_values

    def run(self) -> tuple[str, any]:
        """Presents the multiple-choice options enumerated.

        Returns:
            dict[str, any]: Dictionary mapping this component's ID to output.
        """
        while True:

            selection = self.enumchoices(self.prompt, self.options)

            # Run the selection before returning if it is a UICompnent
            if issubclass(type(selection), CLIComponent):
                selection = selection.run()

            output = (self.id, selection)

            if self.pass_values:
                self.pass_values(output[1])

            if not self.root:
                return output

# ---------------------------------------------------------------------------------------------------------------------


class UserInput(CLIComponent):
    """A CLIComponent that prompts the user for input and validates it.

    Args:
        id (str): Identifier for this input field.
        prompt (str): Text prompt to show the user.
        **constraints: Keyword arguments for validation constraints.
        See `CLIComponent.prompt_user`.
    """

    def __init__(self, *, id: str, prompt: str, **constraints):
        self.id = id
        self.prompt = prompt
        self.constraints = constraints
        self.private_prompt = constraints.get('private', False)

    # Prompts the user for input, validating with properties
    def run(self) -> dict[str: any]:
        """Prompts and validates user input.

        Returns:
            dict[str, any]: Dictionary mapping this component's ID to value.
        """
        ans = self.prompt_user(self.prompt, self.constraints, self.private_prompt)
        return {self.id: ans}
