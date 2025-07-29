import pandas as pd
from contextlib import contextmanager
import random


class show_full_df(pd.option_context):
    def __init__(self, full_column=False, *args):
        arguments = ["display.max_rows", None, "display.max_columns", None]
        if full_column:
            arguments = arguments + ["display.max_colwidth", None]
        super().__init__(*arguments, *args)


def specific_columns_df(df, columns):
    """Returns a dataframe with only specified columns kept"""
    if not hasattr(columns, "__len__"):
        columns = [columns]
    return df.drop([col for col in df.columns if col not in columns], axis=1)


@contextmanager
def display_and_clear():
    from IPython.display import display, update_display, Markdown

    def _wrap(item):
        nonlocal to_clear
        id = str(hash(random.random()))
        display(item, display_id=id)
        to_clear.append(id)

    to_clear = []
    try:
        yield _wrap
    finally:
        for id in to_clear:
            update_display(Markdown(""), display_id=id)


def return_module(module_path):
    module_name = module_path.split(".")[-1]
    module_parent = __import__(module_path, fromlist=[module_name])
    return module_parent
