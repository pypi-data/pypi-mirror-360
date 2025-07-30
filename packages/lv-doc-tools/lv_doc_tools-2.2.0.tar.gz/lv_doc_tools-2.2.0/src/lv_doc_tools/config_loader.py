"""
Doc Generator
==============

An object that handles creating docs for labview projects.



"""
from pathlib import Path, PureWindowsPath, PurePosixPath
import os
import json


class Doc_Config_Loader:
    """
    This class loads and populates config file for lv_doc_tool libraries. 
    It populates paths with defaults if none given in config file.
    

    :param config_path: a path to a configuration json file, e.g. config.json

    The config is a dictionary with the following fields:

    .. code:: python

        "PATHS": {
        "ROOT": "PATH_TO_PROJECT_FOLDER",
	    "LV_PROJ": "THE_PROJECT.lvproj",
	    "TESTS": "RELATIVE PATH TO TESTS",
	    "OUTPUT": "relative_path_to_output_folder",
	    "CARAYA": "Absolute Path_to_Caraya_toolkit",
	    "TEST_XML": "relative path to test xml output",
	    "DOC_SOURCE": "relative path to additional adoc files, e.g converted xml",
	    "ANTIDOC_CONFIG":"rel_path_to_antidoc.config"
        },
        "TEST_ITEMS": {
                        "module_name": ["relative_path_to/test1.vi", "relative/testFolder2_for_all_vi/in_folder"],
                        "module2_name": ["relative/testFolder3"]
                        },
        "EMAIL": "info@resonatesystems.com.au",
        "AUTHOR": "Resonate Systems",
        "PAGE_TITLE": "A string"

    """

    def __init__(self, config):
        """
        Constructor method, the following fields in config are required

        * 'config': either dictonary with config (loaded already from json) 
                    or Path to the config file, e.g. config.json
        """
        if isinstance(config, (Path, str, PureWindowsPath, PurePosixPath)):
            if os.path.exists(config):
                try:
                    with open(config, "r", encoding="utf-8") as config_file:
                        config_dict = json.load(config_file)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from config file: {e}")
                    raise
            else:
                raise FileNotFoundError(f"Config file not found: {config}")
        elif isinstance(config, dict):
            config_dict = config
        else:
            raise TypeError("Config must be a path to a JSON file or a dictionary.")
        
        try:
            self.add_config_paths(config_dict["PATHS"])
            self.add_attributes(config_dict)
        except Exception as e:
            print(f"Config error: {e}")
            raise

    def add_config_paths(self, config):
        """
        Create Path() objects from the config paths dictionary.
        Set default values if items not present.
        Raise error if mandatory items not present, e.g. lv_proj_path.
        """
        required_keys = ['ROOT', 'LV_PROJ']
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise KeyError(f"Missing required config key(s): {', '.join(missing)}")
        
        self.root = Path(config["ROOT"]).resolve()
        paths = {}

        # Setting lv_proj as required in defaults
        paths['lv_proj'] = self.root / config["LV_PROJ"]

        # Optional paths with defaults
        defaults = {
            'tests': "Tests",
            'caraya': PureWindowsPath(
                "C:\\Program Files\\National Instruments\\LabVIEW 2025\\vi.lib\\addons\\_JKI Toolkits\\Caraya\\CarayaCLIExecutionEngine.vi"
            ),
            'antidoc_config': paths['lv_proj'].stem + ".config",
        }

        # define keys relative to root
        relative_keys = ['tests', 'output', 'doc_source', 'adoc_theme', 'antidoc_config',"exported_gaphor_diagrams"]
        for key in relative_keys:
            if key.upper() in config:
                paths[key] = self.root / config[key.upper()]
            elif key in defaults:
                val = defaults[key]
                paths[key] = self.root / val if isinstance(val, str) else val

        # caraya path is absolute or manually overridden
        if "CARAYA" in config:
            paths['caraya'] = Path(config["CARAYA"])

        # test_xml is relative to tests path
        if "TEST_XML" in config:
            paths['test_xml'] = paths['tests'] / config["TEST_XML"]

        if "GAPHOR_MODEL" in config:
            paths["gaphor_model"]= Path(config["GAPHOR_MODEL"])

        self.paths = paths

    def add_attributes(self, config):
        """
        Handle non pathitems from the config.
        Set defaults if items are missing
        """

        self.author = config.get("AUTHOR", "Resonate Systems")
        self.email = config.get("EMAIL", "info@resonatesystems.com.au")
        self.title = config.get("TITLE", f"Documentation For {config['PATHS']['LV_PROJ']}")

        # Handle tests configuration
        tests_config = config.get("TESTS")
        if tests_config:
            test_suites = {}
            for suite_name, test_list in tests_config.items():
                if isinstance(test_list, list):
                    test_suites[suite_name] = [self.paths['tests'].joinpath(x) for x in test_list]
                elif isinstance(test_list, str):
                    test_suites[suite_name] = self.paths['tests'].joinpath(test_list)
                self.tests = test_suites
        else:
            self.tests = {}

        self.confluence = config.get("CONFLUENCE")

if __name__ == "__main__":

    CONFIG_PATH = "C:\\Users\\Resonate Systems\\Documents\\repos\\lv_doc_tools\\src\\lv_doc_tools\\config.json"
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        print(config)

    mydocloader=Doc_Config_Loader(config)
    print("\nResolved Paths:")
    for key, value in mydocloader.paths.items():
        print(f"{key}: {value}")