#from __future__ import with_statement
import yaml
import os
import re

class ConfigFile:
    def __init__(self):
        self.config_fname = ""
        self.loaded = False
        self.config_data = {}

    def load(self, fname="config.cfg"):
        try:
            with open(fname, 'r') as configfile:
                    self.config_data = yaml.load(configfile)
        except Exception as error:
            print "Error in configuration file:"
            print "\t", error
        self.config_fname = fname
        self.loaded = True


    def add_section(self, section, opts, dic=None):
        if dic is not None:
            dic[section] = opts
        else:
            self.config_data[section] = opts

class ConfigGenerator:
    def __init__(self, config_file):
        self.config_file = config_file
        self.template_base_dir = "templates"
        self.template_dir = ""
        self.files = []
        self.section = ""
        self.opts = {}
        self.actual_opts = {}
        self.computed_opts = {}

    def generate(self):
        self._check_opts(self.actual_opts, self.opts)
        for f in self.files:
            try:
                with open(os.path.join(self.template_dir, f), 'r') as opts_file:
                    self._replace_opts(opts_file)
            except Exception as error:
                print error

    def _check_opts(self, opts_dict, opts_types_dict):
        for opt_name, opt_val in opts_dict.items():
            try:
                types = opts_types_dict[opt_name]
            except Exception as error:
                print "Option not found: ", error
            if type(types) is dict:
                self._check_opts(opts_dict[opt_name], opts_types_dict[opt_name])
            elif type(types) is tuple:
                if type(opt_val) not in types:
                    print "Type not correct in option ", opt_name, " value: ", opt_val
            elif type(types) is str and opt_val not in types.split('|'):
                    print "Type incorrect in option ", opt_name, " value: ", opt_val
                
    def _replace_opts(self, file):
        lines = file.readlines()                                                                                                                                                                                                 
        file_opts = []
        for line in lines:
            line_opts = re.findall(r'\$\[(.+?)\]', line)
            file_opts.extend(line_opts)
        for opt in file_opts:                                                                                                                                                                                                     
            lines = l.replace("$[" + opt + "]", str(self._dots2dict(opt))
        # Save line number and replace

    def _dots2dict(self, opt):
        c = opt.split('.')
        return 1

#TODO: Replace str for func type which parse the str

class OpenFOAMConfigGenerator(ConfigGenerator):
    def __init__(self, config_file):
        ConfigGenerator.__init__(self, config_file)
        self.opts = {"engine": (str,), 
                     "version": (str,), 
                     "solver": (str,), 
                     "mesh": {"ncx": (int,), "ncy": (int,), "ncz": (int,)},
                     "domain" : {"lx": (int, float), "ly": (int, float), "lz": (int, float)}, 
                     "time" : {"start": (float, int), "end": (float, int), "delta": (float, int), "write-interval": (float, int)}, 
                     "parallel": {"npx": (int), "npy": (int), "npz": (int)},
                     "liquid-properties": {"density": (float, str), "viscosity": (float, str)},
                     "boundary-field": {"velocity": {"mode": "fixed-value|zero-gradient|constant-gradient", 
                                                     "x": (float, int, str),
                                                     "y": (float, int, str), 
                                                     "z": (float, int, str)},
                                        "pressure": {"mode": "fixed-value|zero-gradient|constant-gradient",
                                                     "x": (float, int, str),
                                                     "y": (float, int, str), 
                                                     "z": (float, int, str)}},
                     "coupling-opts": {"stress-compute": {"mode": "surface|cell-centre"}}}
        self.section = "CFD-OPTIONS"
        self.actual_opts = self.config_file.config_data[self.section]
        self.foam_version = self.actual_opts["version"]
        self.template_dir = os.path.join(self.template_base_dir, "openfoam/" + self.foam_version)
        self.files = ["0/p", "0/U", "constant/transportProperties", "constant/polyMesh/blockMeshDict",
                      "system/controlDict", "system/decomposeParDict"]
        self.computed_opts = self._compute_foam_options()

    def _compute_foam_options(self):
        computed_opts = {}
        npx = self.actual_opts["parallel"]["npx"] 
        npy = self.actual_opts["parallel"]["npy"] 
        npz = self.actual_opts["parallel"]["npz"] 
        computed_opts["num-subdomains"] = npx * npy * npz
        return computed_opts



#TODO: Add temperature and options based on the solver, eg. if density or temperature options has to be
       # taken into account

coupling_opts = {"timeste-ratio": int, "units": "lj|real", "coupling-unit": {"x-unit": float, 
                 "y-unit": float, "z-unit": float}, "const-region": {"lower-cell": int, "upper-cell": int},
                 "boundary-region": {"lower-cell": int, "upper-cell": int}, "coupling-region": {"cells": int}}
        

if __name__ == "__main__":
    config_file = ConfigFile()
    config_file.load()
    c = OpenFOAMConfigGenerator(config_file)
    c.generate()

