# -*- coding: utf-8 -*-
"""

Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Thu Nov 10 14:12:04 2022
@author: Timothe
</div>
"""

import os
from configparser import ConfigParser, NoOptionError
import json
import numpy as np


class TwoLayerDict(dict):
    def __init__(self, value={}):
        """
        A class that forces a two layer indexing dictionnary.
        each value must have two keys in the dictionnary.
        It is usefull to have a datatype in ram based on a basic python datatype (dictionnary)
        and ensure that is it at all time compatible with an .ini config file.
        See ConfigFile class for more details on this aspect.

        Parameters
        ----------
        value : dictionnary, optional
            The dictionnary object to initiate the class with. It must be compliant with the rule :
            each value must have two keys
            e.g. be nested into two dictionanries. Example :
                valid_dict = {"first_layer_key" : {"second_layer_key" : value1, "another_sedonc_layer_key" : value2}}
            The default is an empty dictionnary : {}.

        Returns
        -------
        None.

        Timothe Jost - 2021
        """

        self._assert_two_layers(value)
        super().__init__(value)

    def pop(self, *args):  # fisrt argument is indices or index (list or scalar)
        # second argument is default value to te returned if key pair is not in dict
        index = args[0]
        try:
            outindex, inindex = self._assert_index(index)
        except ValueError:
            outindex, inindex = index, None

        if inindex is None:  # only an outerkey has been supplied. Poping the whole layer 2 for that outer key
            c_args = (outindex, *args[1:])
            default = super().pop(*c_args)
        else:  # outer and inner key supplied, popping out a specific value in layer two.
            try:
                c_args = (inindex, *args[1:])
                default = self[outindex].pop(*c_args)
            except KeyError:  # outindex is not in self.keys()
                try:
                    default = args[1]  # return default value if supplied
                except IndexError:
                    raise KeyError(f"Key pair {outindex}, {inindex} not in dictionnary")

        self._values_changed_callback()
        return default

    def get(self, outer, inner, *args):
        try:
            return super().__getitem__(outer)[inner]
        except KeyError:
            try:
                return args[0]  # return default argument if it exists
            except IndexError:
                raise KeyError(f"Key pair {outer}, {inner} not in dictionnary")

    def update(self, value):

        self._assert_two_layers(value)
        for key, val in value.items():
            try:
                self[key].update(val)
            except KeyError:
                super().__setitem__(key, val)
        self._values_changed_callback()

    def __getitem__(self, index):
        try:
            outindex, inindex = self._assert_index(index)
        except ValueError:
            return super().__getitem__(
                index
            )  # only one index supplied, return the whole second layer correspuunding to outer key

        return super().__getitem__(outindex).__getitem__(inindex)  # double indexing : two keys for value access

    def __setitem__(self, index, value):
        try:
            outindex, inindex = self._assert_index(index)
        except ValueError:  # only one index supplied, acess the whole second layer correspuunding to outer key
            outindex, inindex = index, None

        if inindex is None:
            if isinstance(value, dict):
                super().__setitem__(outindex, value)
            else:
                raise ValueError("Cannot assign a non dictionnary to a single key")
        else:
            try:
                self[outindex].update({inindex: value})
            except KeyError:  # if outindex is not in self.keys()
                super().__setitem__(outindex, {inindex: value})

        self._values_changed_callback()

    def __getattr__(self, key):
        if key in self.keys():
            return self[key]
        else:
            raise KeyError(f"TwoLayerDict has no key {key} at first level")

    def __setattr__(self, key, value):
        if not isinstance(value, dict):
            raise TypeError("a value assigned to a section must be a dictionnary")

        if key in self.keys():
            self[key].update(value)
        else:
            self[key] = value
        self._values_changed_callback()

    def _values_changed_callback(self):
        # TODO : optimisation for calling it only once per update is possible.
        # Need to momemntarily disable callback from setitem when called from and other setters
        # that themlselved callsetitem posibly multiple times.
        # is there a risk of discrepancy between data in ram and data on drives in that case ?
        # an empty callback called whenever a value changed.
        # Can be used in class deriving, and in particular ConfigFiles
        pass

    @staticmethod
    def _assert_two_layers(value):  # verifies that value is a valid two layer dictionnary
        if isinstance(value, TwoLayerDict):
            return True
        if not isinstance(value, dict):
            raise TypeError("A TwoLayerDict dictionnary must be dictionnary")
        for key in value.keys():
            if not isinstance(value[key], dict):
                raise ValueError(f"Each value in a TwoLayerDict must have two keys, not the case for key :'{key}'")

    @staticmethod
    def _assert_index(
        index,
    ):  # verifies that the index has two separate keys. First one being outer layer and second one being inner
        if isinstance(index, (list, tuple)) or len(index) == 2:
            return index[0], index[1]
        else:
            raise ValueError("TwoLayerDict must be indexed with two keys")

    def __str__(self):
        out = "{\n"
        for key in self.keys():
            out += str(key) + " : {\n"
            for skey in self[key]:
                out += "\t" + str(skey) + " : " + str(self[key][skey]) + ",\n"
            out += "\t},\n"
        out += "}"
        return out

    def __repr__(self):
        return self.__str__()


class ConfigFile(TwoLayerDict):
    def __init__(self, path, **kwargs):
        """
        A class to access config files through an object with indexing,
        either for geting or seting values.
        Seamless and easy integration in code, ability to load or set multiple
        variables at once for more readability when using in static environments.

        (e.g. functions or simple classes)

        If not existing, the file will be created (but folder must exist)
        when key values are assigned.

        Python standard variables are supported, as well as numpy arrays, internally
        represented as nested lists. Avoid using complex numpy structures as they could be
        erroneously loaded from file. (no specific dtypes support #TODO)

        Parameters
        ----------
        path : str
            Path to the config file.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        A variable which is also a handle to the file.
        Can be used to load values with tho text indexes (two layer dictionary)
        or set values in the same way (immediately applies changes to the text file on setting variable value)
        """
        super().__init__({})

        super(dict, self).__setattr__("path", os.path.abspath(path))
        super(dict, self).__setattr__("cfg", ConfigParser())
        # called this way to bypass the __setattr__ overload in parent class
        # TwoLayerDict that sets key values pair to the dict with the setattr dot syntax.

        if os.path.isfile(self.path):
            self._read()
        else:
            self._write()

    def refresh(self):
        # fully regenerate dictionnary in ram from the values present in the file at self.path
        self._read()

    def flush(self):
        self._write()

    # def couples(self):
    #    sections = self.sections()
    #    result = []
    #    [ result.extend( [ ( section, param ) for param in self.params(section) ] ) for section in sections ]
    #    return tuple(result)

    # def sections(self):
    #    return self.keys()
    #    return self.cfg.sections()

    # def params(self,section = None):
    #    return self[section].keys()
    #    #return self.cfg.options(section)

    def _clear_cfg(self):
        for section in self.cfg.sections():
            self.cfg.remove_section(section)

    def _create_sections(self):
        for section in self.keys():
            if section not in self.cfg.sections():
                self.cfg.add_section(section)

    def _values_changed_callback(self):
        # this method is called each time a value is changed by any means in the dictionnary
        self._write()

    def _write(self):
        """
        Question:
            #TODO
            Make sure we can load many variables types correctly by saving them with pickle dumping in str format.
            And loading from str with pickle, instead of creating a custom "key type" with json.
            Or see if we can jsonize pandas dataframes easily. Could be an idea too.
            In that case though, we need to jsonize arrays in a better way, including dype.
            Need to see if numpy doesn't have that ability built in.'
        Returns:
            TYPE: DESCRIPTION.

        """

        def jsonize_if_np_array(value):
            if (value.__class__.__module__, value.__class__.__name__) == ("numpy", "ndarray"):
                array = ["np.ndarray", value.tolist()]
                return array
            return value

        def ini_compat_json_dumps(_value):
            if isinstance(value, str):
                _value = _value.replace("%", "%%")
            return json.dumps(_value)

        # self._write_callback()
        self._clear_cfg()
        self._create_sections()
        for section in self.keys():
            for param in self[section].keys():
                value = jsonize_if_np_array(self[section, param])
                self.cfg.set(section, param, ini_compat_json_dumps(value))
        with open(self.path, "w") as configfile:
            self.cfg.write(configfile)

    # def _write_callback(self):
    #    pass

    def _read(self):
        self.cfg.read(self.path)
        super().clear()
        for sec in self.cfg.sections():
            dict.__setitem__(self, sec, {param: self._getasvar(sec, param) for param in self.cfg.options(sec)})
        # self.last_mtime =  os.stat(self.path).st_mtime

    def _getasvar(self, section, param):
        def unjsonize_if_np_array(array):
            if isinstance(array, list):
                if len(array) == 2:
                    if array[0] == "np.ndarray":
                        import numpy as np

                        value = np.array(array[1])
                        return value
            return array

        try:
            # print(section,param)
            # print(self.cfg.get(section,param))
            val = json.loads(self.cfg.get(section, param))
            val = unjsonize_if_np_array(val)
        except NoOptionError:
            return None
        if isinstance(val, str):
            if val[0:1] == "f":
                val = val.replace("''", '"')
        if isinstance(val, list):
            if len(val) == 2:
                if val[0] == "np.ndarray":
                    val = np.array(val[1])
        return val

    def __str__(self):
        return "ConfigFile at: " + self.path + "\n" + super().__str__()
        # return str([ str(key) + " : "+
