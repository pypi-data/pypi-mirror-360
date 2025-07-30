import os
from pathlib import Path
import glob
import json
import shutil
from lv_doc_tools.config_loader import Doc_Config_Loader

class Cleaner:
    def __init__(self,config):
        """
        Constructor for the class

        Args:
            config (dict or Path): a dictionary with config or a path to the config file
        """
        print(f"Config: {config}")
        self.config = Doc_Config_Loader(config)
        self.output_dir=self.config.paths['output']
       
    def clean_output_dir(self):
        """
        This method removes the generated files and folders for a clean start
        """
        file_extensions=[".adoc",".pdf",".xlsx"]
        for file in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, file)
            if os.path.isfile(file_path) and any(file.endswith(ext) for ext in file_extensions):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

        folder_names = ["Images", "includes"]
        for folder in folder_names:
            folder_path = os.path.join(self.output_dir, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")

if __name__=="__main__":
    CONFIG_PATH = "C:\\Users\\Resonate Systems\\Documents\\repos\\rs24016-hitachi-testing\\docs\\config.json"
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    mycleaner=Cleaner(config)
    mycleaner.clean_output_dir()

