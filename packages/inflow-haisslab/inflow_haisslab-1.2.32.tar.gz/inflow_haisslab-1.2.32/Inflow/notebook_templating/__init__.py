from rich.prompt import Prompt, Confirm
from rich.text import Text
from pathlib import Path
from dataclasses import dataclass
import json
from re import sub as regex_replace, compile
from argparse import ArgumentParser
from importlib import import_module
import subprocess

from logging import getLogger

from typing import List, Callable, Set

logger = getLogger("notebook_templates")


def prompter(
    instruction: str,
    default="",
    password_mode=False,
):

    if default:
        adjective = "generated" if password_mode else "default"
        password_help = Text(" (", style="turquoise2").append(
            f"press enter to use the {adjective} one:", style="grey50"
        )
    else:
        password_help = ""

    return Prompt.ask(
        Text("", style="bright_yellow").append("❓ ").append(instruction).append(password_help),
        default=default,
        password=password_mode,
    )


class KeywordsStore(dict):

    filename = "input_fields.json"

    def __init__(self, *args, instanciator: "VariableInstanciator", **kwargs):
        """Initialize the class with a manager.

        Args:
            *args: Variable length argument list for the superclass initialization.
            manager (Installation): An instance of the Installation class that manages this instance.
            **kwargs: Variable length keyword argument list for the superclass initialization.
        """
        self.config_path = Path.home() / "Downloads" / "inflow_notebooks_templating"
        self.instanciator = instanciator
        super().__init__(*args, **kwargs)
        self.load()

    @property
    def path(self):
        """Returns the full path to the configuration file.

        This method constructs the full path by combining the configuration
        directory path managed by the manager with the filename of the
        configuration file.

        Returns:
            Path: The full path to the configuration file.
        """
        return self.config_path / self.filename

    def __setitem__(self, key, value):
        """Sets the value for a given key in the object and saves the state.

        Args:
            key: The key for which the value is to be set.
            value: The value to be associated with the key.

        This method overrides the default behavior of setting an item by calling
        the superclass's __setitem__ method and then saving the current state
        of the object.
        """
        super().__setitem__(key, value)

        getter = self.get_keyword_getter(key)
        if getattr(getter, "save_value", False):
            self.save()

    def __getitem__(self, key) -> str:
        """Retrieve an item from the KeywordsStore.

        This method overrides the __getitem__ method to fetch a keyword from the
        KeywordsStore. If the manager is in reconfiguration mode or the key is not
        present, it loads the necessary data and retrieves the value using a getter
        function.

        Args:
            key (str): The key for the item to retrieve from the KeywordsStore.

        Returns:
            The value associated with the specified key.

        Raises:
            KeyError: If the key is not found in the KeywordsStore after attempting
            to retrieve it.

        Notes:
            This method logs a comment indicating the retrieval of the keyword and
            the current state of the KeywordsStore.
        """

        def update_value():
            if requirements:  # populate the getter's requirements before acessing the getter's value here
                [self[requirement] for requirement in requirements]
            value = getter()
            self[key] = value

        if not self.instanciator.reconfigure:
            self.load(key)
        logger.debug(f"Getting keyword {key} from the KeywordsStore containing {dict(self)}")
        getter = self.get_keyword_getter(key)
        requirements = getattr(getter, "requirements", [])
        if self.instanciator.reconfigure or key not in self.keys() or (key in self.keys() and requirements):
            update_value()
        return super().__getitem__(key)

    def load(self, key=None):
        """Load data from a JSON file into the object.

        This method reads a JSON file from the specified path and loads its contents into the object.
        If a specific key is provided, only the value associated with that key will be loaded.
        If the key is not found or if no key is specified, all key-value pairs from the JSON file will be loaded.

        Args:
            key (str, optional): The specific key to load from the JSON file.
                                 If None, all key-value pairs will be loaded.

        Returns:
            None: This method does not return a value.

        Raises:
            FileNotFoundError: If the specified path does not point to a valid file.
        """
        if not self.path.is_file():
            return
        with open(self.path, "r") as f:
            fields: dict = json.load(f)
        for loaded_key, value in fields.items():
            if key is None or (loaded_key == key and getattr(self.get_keyword_getter(key), "save_value", False)):
                super().__setitem__(loaded_key, value)

    def save(self):
        """Saves the current object state to a JSON file.

        This method creates the necessary parent directories for the file if they do not exist,
        and then writes the object's dictionary representation to the specified path in JSON format
        with an indentation of 4 spaces.

        Attributes:
            path (Path): The file path where the object state will be saved.

        Raises:
            IOError: If there is an error writing to the file.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        dict_to_save = dict(self)
        selected_keys = []
        for key in dict_to_save.keys():
            key_function = self.get_keyword_getter(key)
            if getattr(key_function, "save_value", False):
                selected_keys.append(key)
        dict_to_save = {key: value for key, value in dict_to_save.items() if key in selected_keys}
        with open(self.path, "w") as f:
            json.dump(dict_to_save, f, indent=4)

    def get_keyword_getter(self, keyword) -> Callable[..., str]:
        """Retrieves a getter method for a specified keyword from the manager.

        This function looks for a method in the manager associated with the given keyword.
        If the method is not found, it raises a ValueError.

        Args:
            keyword (str): The name of the keyword for which to retrieve the getter method.

        Returns:
            Callable[..., str]: The getter method associated with the specified keyword.

        Raises:
            ValueError: If no getter method is configured for the specified keyword.
        """
        getter = getattr(self.instanciator, keyword, None)
        if getter is None:
            raise ValueError(f"You didn't configured a getter method for the variable {keyword}")
        return getter

    # @property
    # def keywords_list(self) -> Set[str]:
    #     from .files import TemplatedFile

    #     keywords = [
    #         keyword
    #         for container in self.manager.containers
    #         for file in container.files
    #         if isinstance(file, TemplatedFile)
    #         for keyword in file.keywords
    #     ]
    #     keywords.extend(
    #         [keyword for file in self.manager.files if isinstance(file, TemplatedFile) for keyword in file.keywords]
    #     )
    #     return set(keywords)

    # def validate_keywords_list(self):
    #     for keyword in self.keywords_list:
    #         if not hasattr(self.manager, keyword):
    #             raise ValueError(f"You didn't configured a getter method for the variable {keyword}")
    #     for keyword in self.manager.reset_values:
    #         if not hasattr(self.manager, keyword):
    #             raise ValueError(f"The variable {keyword} doesn't exist and cannot be reset.")

    # def populate(self):
    #     for keyword in self.keywords_list:
    #         self[keyword]
    #     self.manager.reset_values = []


class TemplatedNotebook:

    flag = r"%%"

    def __init__(self, source_path: str | Path, variable_instanciator: "VariableInstanciator") -> None:
        self.source_path = Path(source_path)
        self.instanciator = variable_instanciator

    def get_content(self) -> str:
        """Retrieves and processes the content from a specified source file.

        This method opens a file located at `self.source_path`, reads its contents,
        and replaces occurrences of specified keywords with their corresponding values
        using the `replace_keyword` method.

        Returns:
            str: The processed content with keywords replaced.
        """
        with open(self.source_path, "r") as f:
            content = f.read()
        return content

    def find_keywords(self, content: str):

        keywords_finder = compile(rf"{self.flag}(.*){self.flag}")
        keywords = set(keywords_finder.findall(content))
        return keywords

    def apply_replacements(self):
        content = self.get_content()
        for keyword in self.find_keywords(content):
            content = self.replace_keyword(keyword, content)
        return content

    def replace_keyword(self, keyword: str, content: str):
        """Replace a specified keyword in the given content with its corresponding value.

        This method checks if the provided keyword is registered in the class's keywords.
        If the keyword is not found in the class definition, it raises a ValueError.
        If the keyword is valid, it retrieves the associated value from the keywords store and replaces
        occurrences of the keyword in the content using a regex pattern.

        Args:
            keyword (str): The keyword to be replaced in the content.
            content (str): The content in which the keyword will be replaced.

        Raises:
            ValueError: If the keyword is not registered in the class's keywords.

        Returns:
            str: The content with the keyword replaced by its corresponding value.
        """
        value = self.instanciator.store[keyword]
        pattern = f"{self.flag}({keyword}){self.flag}"
        return regex_replace(pattern, str(value), content)


def save_value(func):
    func.save_value = True
    return func


@dataclass
class VariableInstanciator:

    def __init__(self):
        self.store = KeywordsStore(instanciator=self)

    reconfigure: bool = False

    def SESSION_NAME(self):
        return prompter("Enter session_name")

    @save_value
    def workspace_path(self):
        return prompter("Enter the filepath of the workspace you want to use for the vscode window")

    @save_value
    def vscode_binary_path(self):
        possible_location = Path.home() / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd"
        if not possible_location.is_file():
            return prompter("Enter the filepath of vscode binary executer (example:)", default=str(possible_location))
        return str(possible_location)


def run_notebook_templating(*args):
    from one import ONE as Connector

    parser = ArgumentParser()
    # parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Force fixing problematic files by rewriting them from scratch if any error is found. "
        "Be carefull to not use this command if you want to ensure you keep valueable "
        " settings written in the files located in the config folder.",
    )
    parser.add_argument("-s", "--session", default=[], nargs="+")
    parser.add_argument("-p", "--project", default="ResearchProjects.adaptation")
    parser.add_argument("-n", "--names-pattern", default="*")

    args = parser.parse_args()

    project = args.project
    connector = Connector(data_access_mode="remote")

    for session_name in args.session:

        instanciator = VariableInstanciator()

        if args.session:
            instanciator.store["SESSION_NAME"] = session_name
        else:
            session_name = instanciator.store["SESSION_NAME"]

        logger.info(f"Searching for session {session_name}")
        session_path_str: str = connector.search(id=session_name, details=True, no_cache=True).path  # type: ignore
        session_path = Path(session_path_str)
        logger.info(f"Found the session {session_name} and it's root at {session_path}")

        module = import_module(project + ".notebook_templates")
        module_path = Path(str(module.__path__[0]))
        logger.info(f"Module path loaded : {module_path}")

        notebooks_found = set()
        for notebook_file in module_path.glob(f"{args.names_pattern}.ipynb"):

            new_path_dir = session_path / "notebooks"
            new_path_dir.mkdir(parents=False, exist_ok=True)
            new_path = new_path_dir / notebook_file.name
            notebooks_found.add(new_path)

            if new_path.is_file():
                continue

            new_file_content = TemplatedNotebook(notebook_file, instanciator).apply_replacements()
            with open(new_path, "w") as file:
                file.write(new_file_content)
            logger.info(f"Wrote {new_path}")

        for notebook_file in (session_path / "notebooks").glob(f"{args.names_pattern}.ipynb"):
            notebooks_found.add(notebook_file)

        logger.info("Opening vscode notebooks")
        notebooks = [str(notebook) for notebook in notebooks_found]
        workspace_path = instanciator.store["workspace_path"]
        subprocess.run([instanciator.store["vscode_binary_path"], "--new-window", workspace_path] + notebooks)
