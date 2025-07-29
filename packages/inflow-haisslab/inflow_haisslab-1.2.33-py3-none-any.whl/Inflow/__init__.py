__version__ = "1.2.33"

# external imports
import os, sys

# one level down imports
from . import signal
from . import tdms
from . import tiff
from . import path
from . import plots
from . import ios
from . import masks
from . import pandex

# specific shortcut imports
from .ios import load
from .ios import load as read
from .ios import save
from .ios import save as write
from .core import logging, config, decorators, optimization, pipelining, special_types, time, utils


def ask_for_session_label_gui():
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()  # hide the main root window

    # create a simple dialog that asks for a string
    session_label = simpledialog.askstring(title="Session Label", prompt="Please enter session label:")
    return session_label


def run_suite2p_gui_asking_session():
    import one

    connector = one.ONE(data_access_mode="remote")
    session_label = ask_for_session_label_gui()
    print(f"{session_label=}")
    session_id = connector.to_eid(session_label)
    print(f"{session_id=}")
    session_details = connector.search(id=session_id, details=True)
    run_suite2p_gui(session_details, allow_blank=False)


def run_suite2p_gui(session_details=None, plane=0, statfile=None, allow_blank=True):
    from suite2p import gui as suite2p_gui_module
    from PyQt5 import QtWidgets

    if statfile is None:
        from .ios.helpers import get_suite2p_path
        from logging import getLogger

        try:
            statfile = get_suite2p_path(session_details=session_details, plane=plane, file="stat\\.npy")[0]
            getLogger().load(f"Opening GUI directly at stat file {statfile}")
        except (
            IndexError,
            ValueError,
            AttributeError,
        ):  # session_details is None or no stat file found at session_details.path
            statfile = None

    if statfile is None and not allow_blank:
        raise ValueError("The session you supplied does not contain a suite2p stat file. Maybe suite2p wasn't run ?")
    try:
        app = QtWidgets.qApp if QtWidgets.QApplication.instance() is None else QtWidgets.QApplication.instance()
        return_value = suite2p_gui_module.run(statfile=statfile)
        if not QtWidgets.QApplication.instance():
            app.quit()
            del app
        return return_value
    except SystemExit:
        return


try:
    import suite2p

    if not hasattr(suite2p, "run_gui"):
        setattr(suite2p, "run_gui", run_suite2p_gui)
except ImportError:  # just skipping this syntaxic sugar if suite2p not installed
    pass


name = "Inflow"
