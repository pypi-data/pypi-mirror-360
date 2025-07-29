# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 15:54:32 2023

@author: tjostmou
"""
import inspect
from functools import wraps
from typing import Mapping, Iterable
from .special_types import AttrDict
from Inflow.core.logging import get_local_logger, LogSession


def filter_kwargs(func):
    @wraps(func)
    def wrap(**kwargs):
        allowed_kwargs = func.__code__.co_varnames[: func.__code__.co_argcount]
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in allowed_kwargs}
        return func(**filtered_kwargs)

    return wrap


def return_as_attr_dict(func):
    """This function is a decorator that wraps another function and returns the result as an AttrDict child class,
    which is a dictionary subclass that allows accessing keys as attributes.

    Args:
        func (callable): A function to be wrapped.

    Returns:
        callable: A decorated function that returns the result of the original function as an AttrDict object.

    Raises:
        NotImplementedError: If the given project is not implemented.

    Examples:
        The following example shows how to use this decorator to wrap the return_dict_func function:

    ``` python
        @return_as_attr_dict
        def return_dict_func(arguments,...):
            ...

        result = return_dict_func("Adaptation")
        print(result.pw10_20)  # Access the value of the "pw10_20" key as an attribute.
        print(result['pw10_20'])  # Access the value of the "pw10_20" key using the traditional dictionary syntax.
    ```
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        return AttrDict(func(*args, **kwargs))

    return wrap


class SignatureEditer:
    _kw_kind = inspect.Parameter.KEYWORD_ONLY

    @staticmethod
    def from_function(function):
        try:
            return SignatureEditer(function.__signature__)
        except AttributeError:
            return SignatureEditer(inspect.signature(function))

    def __init__(self, original_signature=None):
        self.signature = original_signature
        if self.signature is None:
            self.signature = inspect.Signature()

    def remove_var_keyword_params(self):
        new_params = []
        for param in self.signature.parameters.values():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                continue
            new_params.append(param)
        self.signature = inspect.Signature(parameters=new_params, return_annotation=self.signature.return_annotation)
        return self

    def remove_params(self, *keys):
        new_params = [param for name, param in self.signature.parameters.items() if name not in keys]
        self.signature = inspect.Signature(parameters=new_params, return_annotation=self.signature.return_annotation)
        return self

    def _add_params(self, *params):
        """
        Expects already contructed parameters (for example from a list of params extracted from a session)
        """
        new_params = [param for param in self.signature.parameters.values()]
        existing_params_names = [param.name for param in new_params]
        for param in params:
            if param.name in existing_params_names or param.kind not in [
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ]:
                continue  # we don't append the params that have a name that already exists
            if param.kind != inspect.Parameter.KEYWORD_ONLY:
                param = inspect.Parameter(
                    name=param.name,
                    kind=self._kw_kind,
                    default=param.default,
                    annotation=param.annotation,
                )

            new_params.append(param)
        self.signature = inspect.Signature(parameters=new_params, return_annotation=self.signature.return_annotation)
        return self

    def add_params_from_strings(self, *key_value_tuples):
        """
        Expects tuples composed first of a key (str) and optionnaly a default value for that string (any type)
        in second position of the suple. As many tuple "pairs" as necessary can be supplied, separated by commas.
        Only allows for keyword only parameters additions.
        """

        params = []
        for index in range(0, len(key_value_tuples)):
            try:
                param = inspect.Parameter(
                    name=key_value_tuples[index][0],
                    default=key_value_tuples[index][1],
                    kind=self._kw_kind,
                )
            except IndexError:
                param = inspect.Parameter(name=key_value_tuples[index][0], kind=self._kw_kind)
            params.append(param)

        self._add_params(*params)
        return self

    def add_params_from_function(self, function, defaults_only=True):
        """
        Add params to the ones already in the signature.
        """
        self.remove_var_keyword_params()
        ext_sign = inspect.signature(function)

        if defaults_only:
            params = []
            for param in ext_sign.parameters.values():
                if param.default == inspect._empty and param.kind != inspect.Parameter.KEYWORD_ONLY:
                    # if defaults_only : we only accept parameters that are keywords only,
                    continue  # or that are keywords and positionnal but have a default value
                params.append(param)
        else:
            params = ext_sign.parameters.values()

        self._add_params(*params)
        return self

    def __str__(self):
        return self.signature.__str__()

    def __repr__(self):
        return self.__str__()


def pass_matching_kwargs_only(func):
    """A decorator that modifies a function to only pass matching named arguments to it.

    Args:
        func (callable): The function to be wrapped.

    Raises:
        ValueError: If the wrapped function does not allow access to named argument list.

    Returns:
        callable: The wrapper that modifies the function to only pass matching named arguments to it.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        def make_function_specific_kwargs(args_spec):
            args_names = args_spec.args

            # adding names that match *args, in **kwargs
            specific_kwargs = {}
            for arg_name in args_names:
                if arg_name in kwargs.keys():
                    specific_kwargs[arg_name] = kwargs[arg_name]

            # adding names that match *kwonlyargs, in **kwargs
            kwargs_names = args_spec.kwonlyargs
            for arg_name in kwargs_names:
                if arg_name in kwargs.keys() and arg_name not in specific_kwargs.keys():
                    specific_kwargs[arg_name] = kwargs[arg_name]

            # remove potential duplicates in **kwargs, that would be in *args already
            for arg_index in range(len(args)):
                arg_name = args_names[arg_index]
                if arg_name in specific_kwargs.keys():
                    specific_kwargs.pop(arg_name)

            return specific_kwargs

        try:
            args_spec = inspect.getfullargspec(func)
        except ValueError:
            raise ValueError(
                f"The wrapper pass_matching_kwargs_only cannot be used with function {func.__name__}. "
                "This is probably due to the fact this is a built-in function that is written using C primitives, "
                "and as such is doesn't allow to access named arguments list"
            )
        return func(*args, **make_function_specific_kwargs(args_spec))

    return wrapper


def hide_unused_kwargs(func):
    """
    A decorator that removes the `**unused_kwargs` arguments from a function signature.

    Usage:
        @remove_unused_kwargs
        def my_function(arg1, arg2, **unused_kwargs):
            ...

    This decorator modifies the function signature by removing the `**unused_kwargs` arguments,
    which allows the function to be called with arbitrary keyword arguments that are not
    specifically named `unused_kwargs`.

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs = {key: value for key, value in kwargs.items() if key != "unused_kwargs"}
        return func(*args, **kwargs)

    sig = inspect.signature(func)
    params = [p for p in sig.parameters.values() if p.name != "unused_kwargs"]
    new_sig = sig.replace(parameters=params)
    wrapper.__signature__ = new_sig
    return wrapper


def copy_doc_and_signature_from(original_func):
    def decorator(func):
        func.__doc__ = original_func.__doc__
        func.__signature__ = inspect.signature(original_func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def append_doc_and_signature_from(*external_funcs):
    def decorator(func):
        for external_func in external_funcs:
            if func.__doc__ is None and external_func.__doc__ is not None:
                func.__doc__ = external_func.__doc__
            elif func.__doc__ is not None and external_func.__doc__ is not None:
                func.__doc__ += external_func.__doc__
            sig = SignatureEditer.from_function(func)
            sig.add_params_from_function(external_func, defaults_only=True)
            func.__signature__ = sig.signature

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def autoload_arguments(func):
    from ..ios.load import pipeline_function_arguments

    @wraps(func)
    def wraper(*args, **kwargs):
        local_log = get_local_logger("autoload_arguments")
        new_kwargs = {}

        if "session_details" in kwargs.keys():
            session_details = kwargs["session_details"]
            with LogSession(session_details):
                new_kwargs = pipeline_function_arguments(session_details, func)
                if new_kwargs:  # new_kwargs is not empty
                    local_log.info(
                        f"Found some arguments for the function {func.__name__} in pipelines_arguments.json. "
                        "Using them."
                    )
                overrides_names = []
                for key in new_kwargs.keys():
                    if key in kwargs.keys():
                        overrides_names.append(key)
                if overrides_names:
                    local_log.info(
                        f"Values of pipelines_arguments.json arguments : {', '.join(overrides_names)}, "
                        "are overrided by the current call arguments."
                    )

        new_kwargs.update(kwargs)
        return func(*args, **new_kwargs)

    return wraper


def session_to_path_argument(position, keyword=None):
    """Should remove that soon, not a good idea anyway."""

    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            def get_path(path_argument):
                from pandas.core.series import Series

                if isinstance(path_argument, str):
                    return path_argument
                elif isinstance(path_argument, (dict, Series)):
                    return path_argument.path
                raise ValueError("session_argument must be either a full session path or a dict/pandas series")

            try:
                args = list(args)
                args[position] = get_path(args[position])
                return func(*tuple(args), **kwargs)
            except IndexError:
                pass

            try:
                kwargs[keyword] = get_path(kwargs[keyword])
                return func(*args, **kwargs)
            except KeyError:
                raise ValueError(
                    f"session_to_path_argument decorator : None of argument at position {position} or"
                    + f" argument {keyword} allowed to find argument session path or details"
                )

        return wrap

    return decorator


def recurse(func):
    """Decorator to call decorated function recursively if first arg is non-string iterable.

    Allows decorated methods to accept both single values, and lists/tuples of values.  When
    given the latter, a list is returned.  This decorator is intended to work on class methods,
    therefore the first arg is assumed to be the object.  Maps and pandas objects are not
    iterated over.

    Parameters
    ----------
    func : function
        A function to decorate (does not work with class methods)

    Returns
    -------
    function
        The decorated method
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        import pandas as pd

        if len(args) < 1:
            return func(*args, **kwargs)
        first = args[0]
        exclude = (str, Mapping, pd.Series, pd.DataFrame)
        if isinstance(first, Iterable) and not isinstance(first, exclude):
            return [func(item, *args[1:], **kwargs) for item in first]
        else:
            return func(*args, **kwargs)

    return wrap
