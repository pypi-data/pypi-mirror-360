# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:59:18 2023

@author: tjostmou
"""

import os
import pandas as pd
from functools import wraps, partial
import inspect

from .logging import get_local_logger, LogSession, session_log_decorator
from ..ios.load import preprocessed_data as load_preprocessed_data
from ..ios.save import preprocessed_data as save_preprocessed_data
from ..ios.helpers import get_preprocessed_filename
from .optimization import job_context_decorator

from types import ModuleType
from typing import Protocol, Literal, Callable, Mapping

@pd.api.extensions.register_series_accessor("pipeline")
class SeriesPipelineAcessor:
    def __init__(self, pandas_obj) -> None:
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        required_fields = ["path", "subject", "date", "number"]
        missing_fields = []
        for req_field in required_fields:
            if not req_field in obj.index:
                missing_fields.append(req_field)
        if len(missing_fields):
            raise AttributeError(
                f"The series must have some fields to use one acessor. This object is missing fields : {','.join(missing_fields)}"
            )
        
    def subject(self):
        return str(self._obj.subject)

    def number(self, zfill = 3):
        number = str(self._obj.number) if self._obj.number is not None else ""
        number = (
            number
            if zfill is None or number == ""
            else number.zfill(zfill)
        )
        return number

    def alias(self, separator = "_" , zfill = 3 , date_format = None):

        subject = self.subject()
        date = self.date(date_format)
        number = self.number(zfill)

        return (
            subject
            + separator
            + date
            + ((separator + number) if number else "")
        )

    def date(self, format = None):
        if format :
            return self._obj.date.strftime(format)
        return str(self._obj.date)

@pd.api.extensions.register_dataframe_accessor("pipeline")
class DataFramePipelineAcessor:
    def __init__(self, pandas_obj) -> None:
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        required_columns = ["path", "subject", "date", "number"]
        missing_columns = []
        for req_col in required_columns:
            if not req_col in obj.columns:
                missing_columns.append(req_col)
        if len(missing_columns):
            raise AttributeError(
                f"The series must have some fields to use one acessor. This object is missing fields : {','.join(missing_columns)}"
            )

class SessionDetail(pd.Series):
    def __new__(
        cls,
        series=None,
        *,
        subject=None,
        date=None,
        number=None,
        path=None,
        auto_path=False,
        date_format = None,
        zfill = 3,
        separator = "_"
    ):
        if series is None:
            series = pd.Series()

        if subject is not None:
            series["subject"] = subject
        if date is not None:
            series["date"] = date
        if number is not None or "number" not in series.index:
            series["number"] = number
        if path is not None:
            series["path"] = path

        series.pipeline  # verify the series complies with pipeline acessor, then returns

        if series.name is None:
            series.name = series.pipeline.alias(separator = separator, zfill = zfill , date_format = date_format)

        if auto_path:
            series["path"] = os.path.normpath(os.path.join(
                series["path"],
                series.pipeline.subject(),
                series.pipeline.date(date_format),
                series.pipeline.number(zfill)
            ))

        if not "alias" in series.index:
            series["alias"] = series.pipeline.alias(separator = separator, zfill = zfill , date_format = date_format)

        return series

class Sessions(pd.DataFrame):
    def __new__(cls, series_list):
        # also works seamlessly if a dataframe is passed and is already a Sessions dataframe.
        df = pd.DataFrame(series_list)

        df.pipeline  # verify the df complies with pipeline acessor, then returns

        return df

class FunctionBlock(Protocol):
    def __call__(self, *args, **kwargs) -> Mapping | Callable | None:
        """The callable that is used as a block.
        It can return data ( a mapping ) in the case of function_type block being :
            Getters, Generators and Raw Blocks
        It can return None in the case function_type is :
            Saver,  Generators with skip = True as argument and data existing on disk.
        It can return None in the case where function_type is :

        This class is defined for typehints, and is not a real class useable at runtime
        """

    function_type = str  # the name of the raw function block, without the type_ prefix (generate_ , get_ , save_)
    function_name = Literal[
        "generator", "raw_block", "getter", "saver"
    ]  # the type of function block functionnalty that this function implements

class OutputData(Protocol):
    """Can be a mapping, iterable, single element, or None.

    This class is defined for typehints, and is not a real class useable at runtime"""

class Wrapper(Protocol):
    """Is a function that takes as input a function, and returns a wrapped version of this function.

    This class is defined for typehints, and is not a real class useable at runtime"""

class Pipelines:
    """
    A class that provides a framework for creating pipelines of arbitrary modules
    # Pipelines Usage Guide

    Pipelines are a powerful tool for processing data in a streamlined manner, performing calculations, and generating processed content that is crucial for subsequent analysis steps. This guide provides comprehensive documentation on effectively using pipelines in your workflow.

    ## What is Pipelining?

    Pipelining refers to a series of calculations performed on data, where the processed results are essential for subsequent stages of analysis. However, these calculations often require a significant number of parameters that may vary for each session. To avoid the hassle of passing a large number of arguments throughout the functions in every session, pipelines provide a solution.

    Instead of repeatedly passing the arguments, the preprocessing results are generated once and can be easily obtained in subsequent calls using only the `session_details` argument. Additionally, the `session_details` argument helps trace the location of the stored files where the generated results are saved.

    ## Function Structure in Pipelines

    In the pipelines subpackage, each function has its counterparts: `generate` and `get`. These counterparts offer a simplified way of accessing previously generated results in subsequent functions.

    The `generate`-prefixed function generates the required preprocessing results, which are automatically saved on disk for future use. On the other hand, the `get` function retrieves the previously generated results using only the `session_details` argument.

    ## Determining if a Newly Written Function Should be Pipelined

    To determine whether a function should be part of a pipeline or remain as a normal function, consider the following rationale:

    - **Size of the returned structure**: Functions that do not return a large structure occupying significant space are suitable for pipelining. Typically, these functions generate temporary large structures to extract smaller processed data. It is important to note that pipeline functions automatically save their output to disk upon completion, which may consume more storage space as the functions are called. The processed data that we want to keep is usually smaller, and it is this function responsible for generating this somewhat smaller processed data that should be pipelined. It can internally call functions that generate large data structures in RAM (not on disk) as long as these large data structures remain local to the function (and are discarded as the function returns the small preprocessed data).
    - **Structured information**: If a function computes newly processed data that is well-structured in relation to previously extracted information, it is more appropriate to define it as a normal function. This function can then be called *inside* the pipeline function that generates the input DataFrame, using optional arguments. Another good practice is to add a new column to the DataFrame and return it in a non-pipeline function, which avoids duplicating data in the saved pipeline results. Data duplication can lead to inconsistency issues where two versions of processed data are stored in different locations, making it unclear which version is the "correct" one to use for a particular purpose or contains the most recent changes.

    ## Using Functions in Pipelines

    When using functions within pipelines, keep in mind that using the function's plain name, without the `get` or `generate` prefix, will execute the processing steps without checking for previously generated result files or saving newly processed results. This can be useful for debugging purposes or when working locally without the need to save test results of the function.

    By following these guidelines, you can effectively utilize pipelines in your data processing workflow, reducing the complexity of passing arguments and optimizing the storage of processed results.

    ## Using `multisession` Capabilities

    For pipelines that return DataFrames, you can leverage the `multisession` counterpart in addition to `get` and `generate`. It is more commonly used with `get`. (to avoid complex debugging and have ability to separate arguments per session if required, by using generate in single session mode) This capability allows you to supply a DataFrame of several session details as input, instead of a Pandas Series for `session_details`. Obtaining this DataFrame is straightforward as it is the output of a One connector `search` request.

    **Example:**

    ```python
    import one
    from ResearchProjects import myproject

    connector = one.One()
    sessions = connector.search(subject="mouse12", date_range="2023-05-12")
    session = sessions.iloc[0]

    # This generates trials_df for one session, without loading it if existing, as refresh_main_only is True
    myproject.pipelines.generate_trials_df(arg1, arg2, session_details=my_session_details, refresh_main_only=True)

    # Retrieve trials_df for multiple sessions
    myproject.pipelines.multisession.get_trials_df(session_details)
    ```

    The output of `multisession.get_trials_df` will be a single DataFrame with an added index level corresponding to the session `alias_name`. The `alias_name` is derived from the subject, date, and day number, joined together with underscores, such as `mouse12_2023-05-12_001` for the first session of Mouse 12 on May 12, 2023.

    This DataFrame can then be used as is for single sessions, simplifying the process of consolidating data for end analysis.

    ## Specifics of Using `generate`

    The following arguments can be supplied to the pipeline function with the `generate_` prefix, in addition to the other arguments that the function accepts. The order of the arguments doesn't matter, so they must be provided as keyword named arguments.

    For example, for the pipeline function `pipelines.trials_df(arg1, arg2)`, you can call it like: `pipelines.generate_trials_df(arg1, arg2, session_details=my_session_details, refresh=False)`

    ### Necessary Arguments:

    - `session_details`: This argument contains all the details of a session, such as the subject name, date, root path, JSON details, etc. These details are necessary to reconstruct the path of the saved preprocessed files.

    ### Optional Arguments:

    - `extras`: This argument allows having multiple preprocessed files for a given session with a specific pipelined function. For example, you can have a `neuropil_mask` for C1 or for D1 by specifying `extras="C1"` or `extras="D1"`. The default value is an empty string.
    - `refresh`: By setting this argument to `True`, you can force the function to recompute the results (and save them to a file afterward if `save_preprocessing` is `True`), even if a preprocessing file is found.
    - `refresh_main_only`: Similar to `refresh`, but it only applies to the outermost pipelined function. This can be useful when calling other pipelined functions internally.
    - `skipping`: This argument determines whether to skip loading the file if it is found (or generating if the file is not found). It can be useful if you are not interested in the output at the moment but only want to generate a batch of preprocessed data for sessions that may not already have this preprocessing data saved. The default value is `False`.
    - `save_preprocessing`: This argument determines whether to save the values returned by the function. If `True`, it saves the results and overwrites any existing file with the same name. By default, it is set to `True`.

    ## Specifics of Using `get`

    The `session_details` argument is not necessarily keyword-based in this case. It can be positional and, in that case, should be the first argument.

    ### Necessary Arguments:

    - `session_details`: This argument contains all the details of a session, such as the subject name, date, root path, JSON details, etc. These details are necessary to reconstruct the path of the saved preprocessed files.

    ### Optional Arguments:

    - `extras`: This argument allows having multiple preprocessed files for a given session with a specific pipelined function. For example, you can have a `neuropil_mask` for C1 or for D1 by specifying `extras="C1"` or `extras="D1"`. The default value is an empty string. It must be provided as a keyword named argument and cannot be positional.

    The `get` pipelined functions do not accept any other arguments than the ones specified above. They do not require generating files if not found but raise an `OSError` instead.
    """

    def __init__(self, blocks_module: ModuleType = None) -> None:
        """_summary_

        Args:
            blocks_module (module): The module containing the blocks that the pipeline will use. Initialize without adding a module if blocks_module is set to None (default)

        Attributes:
            blocks_module (module) : The module containing the blocks that the pipeline will use.
            blocks_modules (list) : The list of modules instances that the pipeline will use.
            blocks_functions (set) : The set of functions that the pipeline have dynamically added. They are callables, and their root block name and type is accessible via attributes function_type and function_name.
            multisession (class) : A class that allows to wrap data from multiple sessions using the same syntax as for a single session.
        """
        self.blocks_structure = {}
        # something to keep track of the pipeline architecture as we add more modules to it. It is used at construction, inside attach_blocks, not afterwards. Changing it has no effect on the architecture itself.
        self.blocks_modules = []
        # somthing to keep a link to the different modules we added to this pipeline structure.
        self.blocks_functions = set()
        # somthing to leep track of a set (no duplicates) of functions we added. This is used in external classes relying on pipelines strucure (such as MultisessionGetter)

        if blocks_module is not None:
            self.add_blocks_from_module(blocks_module)

        self.multisession = MultisessionGetter(self)
        # we construct multisession getter after adding some modules. If modules are added externally ouside init via add_blocks_from_module, one must redefine self.multisession again with a call of MultisessionGetter(self)

    def add_blocks_from_module(self, blocks_module: ModuleType) -> None:
        self.blocks_modules.append(blocks_module)
        self.attach_blocks(self.parse_blocks_structure(blocks_module))

    def _get_raw_block(self, block_struct: dict, block_name: str) -> Callable:
        return block_struct["raw_block"]

    def _get_generator(self, block_struct: dict, block_name: str) -> Callable:
        return block_struct["dispatcher"](
            session_log_decorator(
                load_preprocessing(
                    save_preprocessing(
                        job_context_decorator(block_struct["raw_block"]),
                        block_struct["saver"],
                        block_name=block_name,
                    ),
                    block_struct["getter"],
                    block_struct["checker"],
                    block_name=block_name,
                )
            ),
            function_type="generator",
        )

    def _get_getter(self, block_struct: dict, block_name: str) -> Callable:
        if "getter" in block_struct.keys():
            return block_struct["getter"]
        return partial(load_preprocessed_data, alf_identifier=block_name)

    def _get_saver(self, block_struct: dict, block_name: str) -> Callable:
        if "saver" in block_struct.keys():
            return block_struct["saver"]
        return partial(save_preprocessed_data, alf_identifier=block_name)

    def _get_checker(self, block_struct: dict, block_name: str) -> Callable:
        def default_checker(session_details, extra):
            return os.path.isfile(
                get_preprocessed_filename(session_details, block_name, extra)
            )

        if "checker" in block_struct.keys():
            return block_struct["checker"]
        return default_checker

    def _get_dispatcher(self, block_struct: dict, block_name: str) -> Wrapper:
        def _dummy_dispatcher(
            function, function_type: Literal["generator", "getter", "saver"]
        ) -> Callable:
            """
            A placeholder dispatcher function that returns the input function unchanged.

            Args:
                function (Callable): The function to be dispatched.
                function_type (Optional[str]): The function_type or context for the dispatcher.

            Returns:
                Callable: The input function unchanged.
            """
            if not function_type in ["generator", "getter", "saver"]:
                raise ValueError(
                    f"function_type {function_type} is not valid. Should be getter, generator or saver"
                )
            return function

        if "dispatcher" in block_struct.keys():
            return block_struct["dispatcher"]
        return _dummy_dispatcher

    def make_function_block(
        self, function: Callable, function_name: str, function_type: str
    ) -> FunctionBlock:
        # adding attributes to the function themselves allows to treat them more easily than with block_struct
        setattr(function, "function_type", function_type)
        setattr(function, "function_name", function_name)
        return function

    def add_function_block(self, function: FunctionBlock) -> None:
        setattr(self, function.function_name, function)
        self.blocks_functions.add(function)
        # we keep a set (no duplicates) of function that we set, for rease of manupulation in later multisession packer etc.

    def attach_blocks(self, new_blocks_structure: dict) -> None:
        for block_name, block_struct in new_blocks_structure.items():
            block_struct["raw_block"] = self._get_raw_block(block_struct, block_name)
            block_struct["saver"] = self._get_saver(block_struct, block_name)
            block_struct["getter"] = self._get_getter(block_struct, block_name)
            block_struct["checker"] = self._get_checker(block_struct, block_name)
            block_struct["dispatcher"] = self._get_dispatcher(block_struct, block_name)
            # generator must be called last as it uses other block_structs elements to build itself
            block_struct["generator"] = self._get_generator(block_struct, block_name)

            block_struct["names"] = {
                "raw_block": block_name,
                "getter": "get_" + block_name,
                "generator": "generate_" + block_name,
                "saver": "save_" + block_name,
            }

            # block_struct can be used externally to process/debug the details architecture of the pipelines that are existing.
            self.blocks_structure[block_name] = block_struct

            for function_type, function_name in block_struct["names"].items():
                if function_type in ["getter", "saver"]:
                    function = block_struct["dispatcher"](
                        block_struct[function_type], function_type=function_type
                    )
                else:
                    function = block_struct[function_type]
                # adding attributes to the function themselves allows to treat them more easily than with block_struct
                function = self.make_function_block(
                    function, function_name, function_type
                )
                self.add_function_block(function)

    def parse_blocks_structure(self, module: ModuleType) -> dict:
        functions = inspect.getmembers(module, inspect.isfunction)
        blocks_structure = {}
        for function in functions:
            fname = function[0]
            function = function[1]
            if function.__module__ == module.__name__:
                for suffix in ["getter", "saver", "dispatcher", "checker"]:
                    if fname.endswith("_" + suffix):
                        fname = fname.replace("_" + suffix, "")
                        if not fname in blocks_structure.keys():
                            blocks_structure[fname] = {}
                        blocks_structure[fname][suffix] = function
                        break
                else:
                    if not fname in blocks_structure.keys():
                        blocks_structure[fname] = {}
                    blocks_structure[fname]["raw_block"] = function
        return blocks_structure
class BasePipe:
    @staticmethod
    def step1(*args, **kwargs) -> OutputData:
        ...

    @staticmethod
    def _getter(session, extra) -> OutputData:
        ...

    @staticmethod
    def _setter(session, extra, data: OutputData) -> None:
        ...

    @staticmethod
    def _dispatcher():
        ...

    @staticmethod
    def _generator_wrappers():
        ...

    @staticmethod
    def _p_generator():
        ...

    @staticmethod
    def _p_wrapped_getter():
        ...

    @staticmethod
    def _p_wrapped_setter():
        ...

    @staticmethod
    def _logging_wrapper():
        ...


class MultisessionGetter:
    """
    This class provides a method for packing data from multiple sessions.
    It contains a single constructor method called init() and a single static method called multisession_packer().
    The init() method initializes an instance of this class and sets the parent attribute.
    The multisession_packer() method takes in sessions and getter_function as arguments, and returns a dataframe of data from multiple sessions.
    """

    def __init__(self, parent: Pipelines) -> None:
        self.parent = parent
        self.update_blocks()

    def update_blocks(self) -> None:
        block_type_wrappers = {
            "raw_block": self.multisession_raw_block,
            "getter": self.multisession_getter,
            "generator": self.multisession_generater,
            "saver": self.multisession_saver,
        }

        for function in self.parent.blocks_functions:
            wrapped_func = block_type_wrappers[function.function_type](function)
            setattr(self, function.function_name, wrapped_func)

    @staticmethod
    def multisession_getter(function: FunctionBlock) -> Callable:
        def multisession_wrapper(
            sessions: pd.DataFrame, *args, add_session_level: bool = False, **kwargs
        ) -> pd.DataFrame | dict:
            multi_session_data = {}
            for _, session in sessions.iterrows():
                with LogSession(session):
                    multi_session_data[session.u_alias] = function(
                        session, *args, **kwargs
                    )

            return MultisessionGetter.aggregate_multisession_data(
                multi_session_data, add_session_level=add_session_level
            )

        return multisession_wrapper

    @staticmethod
    def multisession_saver(function: FunctionBlock) -> Callable:
        def multisession_wrapper(*args, **kwargs):
            raise NotImplementedError

        return multisession_wrapper

    @staticmethod
    def multisession_raw_block(function: FunctionBlock) -> Callable:
        def multisession_wrapper(*args, **kwargs):
            raise NotImplementedError

        return multisession_wrapper

    @staticmethod
    def multisession_generater(function: FunctionBlock) -> Callable:
        def multisession_wrapper(
            sessions: pd.DataFrame, *args, add_session_level: bool = False, **kwargs
        ) -> pd.DataFrame | dict:
            multi_session_data = {}
            for _, session in sessions.iterrows():
                with LogSession(session):
                    multi_session_data[session.u_alias] = function(
                        session, *args, **kwargs
                    )

            return MultisessionGetter.aggregate_multisession_data(
                multi_session_data, add_session_level=add_session_level
            )

        return multisession_wrapper

    @staticmethod
    def aggregate_multisession_data(
        multisession_data_dict: dict, add_session_level=False
    ) -> pd.DataFrame | dict:
        are_dataframe = [
            isinstance(item, pd.core.frame.DataFrame)
            for item in multisession_data_dict.values()
        ]

        if not all(are_dataframe):
            return multisession_data_dict

        return MultisessionGetter.get_multi_session_df(
            multisession_data_dict, add_session_level=add_session_level
        )

    @staticmethod
    def get_multi_session_df(
        multisession_data_dict: dict, add_session_level: bool = False
    ) -> pd.DataFrame:
        dataframes = []
        for session_name, dataframe in multisession_data_dict.items():
            level_names = list(dataframe.index.names)

            dataframe = dataframe.reset_index()

            if add_session_level:
                dataframe["session#"] = [session_name] * len(dataframe)
                dataframe = dataframe.set_index(
                    ["session#"] + level_names, inplace=False
                )

            else:
                level_0_copy = dataframe[level_names[0]].copy()
                dataframe[level_names[0].replace("#", "")] = level_0_copy
                dataframe["session"] = [session_name] * len(dataframe)

                dataframe[level_names[0]] = dataframe[level_names[0]].apply(
                    MultisessionGetter.merge_index_element, session_name=session_name
                )
                dataframe = dataframe.set_index(level_names)

            dataframes.append(dataframe)

        multisession_dataframe = pd.concat(dataframes)
        return multisession_dataframe

    @staticmethod
    def merge_index_element(
        values: tuple | str | float | int, session_name: str
    ) -> tuple:
        if not isinstance(values, tuple):
            values = (values,)

        new_values = []
        for value in values:
            value = str(value) + "_" + session_name
            new_values.append(value)

        if len(new_values) == 1:
            return new_values[0]
        return tuple(new_values)


def load_preprocessing(
    func: Callable,
    getter: Callable,
    checker: Callable,
    block_name: str = "<pipeline_block>",
):  # decorator to load instead of calculating if not refreshing and saved data exists
    """
    Decorator doctring
    """

    @wraps(func)
    def wrap(session_details, *args, **kwargs):
        """
        Decorator function

        Parameters
        ----------
        *args : TYPE
            DESCRIPTION.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        local_log = get_local_logger("load_pipeline")

        kwargs = kwargs.copy()
        extra = kwargs.get("extra", None)
        skipping = kwargs.pop("skip", False)
        # we raise if file not found only if skipping is True
        refresh = kwargs.get("refresh", False)
        refresh_main_only = kwargs.get("refresh_main_only", False)

        if refresh_main_only:
            # we set refresh true no matter what and then set
            # refresh_main_only to False so that possible childs functions will never do this again
            refresh = True
            kwargs["refresh"] = False
            kwargs["refresh_main_only"] = False

        if refresh and skipping:
            raise ValueError(
                """You tried to set refresh (or refresh_main_only) to True and skipping to True simultaneouly. 
                Stopped code to prevent mistakes : You probably set this by error as both have antagonistic effects. 
                (skipping passes without loading if file exists, refresh overwrites after generating output if file exists) 
                Please change arguments according to your clarified intention."""
            )

        with LogSession(session_details):
            if not refresh:
                if skipping and checker(session_details, extra):
                    local_log.load_info(
                        f"File exists for {block_name}{'.' + extra if extra else ''}. Loading and processing have been skipped"
                    )
                    return None
                local_log.debug(f"Trying to load saved data")
                try:
                    result = getter(session_details, extra=extra)
                    local_log.load_info(
                        f"Found and loaded {block_name}{'.' + extra if extra else ''} file. Processing has been skipped "
                    )
                    return result
                except IOError:
                    local_log.load_info(
                        f"Could not find or load {block_name}{'.' + extra if extra else ''} saved file."
                    )

        local_log.load_info(
            f"Performing the computation to generate {block_name}{'.' + extra if extra else ''}. Hold tight."
        )
        return func(session_details, *args, **kwargs)

    return wrap


def save_preprocessing(
    func: Callable, saver: Callable, block_name: str = "<pipeline_block>"
):  # decorator to load instead of calculating if not refreshing and saved data exists
    @wraps(func)
    def wrap(session_details, *args, **kwargs):
        local_log = get_local_logger("save_pipeline")

        kwargs = kwargs.copy()
        extra = kwargs.get("extra", "")
        save_pipeline = kwargs.pop("save_pipeline", True)

        with LogSession(session_details):
            result = func(session_details, *args, **kwargs)
            if session_details is not None:
                if save_pipeline:
                    # we overwrite inside saver, if file exists and save_pipeline is True
                    saver(result, session_details, extra=extra)
            else:
                local_log.warning(
                    f"Cannot guess data saving location for {block_name}: 'session_details' argument must be supplied."
                )
            return result

    return wrap
