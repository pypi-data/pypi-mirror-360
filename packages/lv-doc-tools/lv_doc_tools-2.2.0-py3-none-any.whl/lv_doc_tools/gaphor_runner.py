import os
import sys
from pathlib import Path
import json

from lv_doc_tools.config_loader import Doc_Config_Loader


gaphor_tools_path = "C:\\Users\\Resonate Systems\\Documents\\repos\\gaphor_tools"
sys.path.insert(0, os.path.join(gaphor_tools_path, "src"))

from gaphor_tools.parsers.diagramexportParser import DiagramExporter


class GaphorRunner:
    
    def __init__(self, config):
       
        self.config = Doc_Config_Loader(config)
        self.gaphor_model_path = self.config.paths["gaphor_model"]
        self.exported_images_path=self.config.paths["exported_gaphor_diagrams"]
        print(self.gaphor_model_path)

        

    def extract_diagrams(self, pattern=".*", format="pdf", export_dir="exported_diagrams"):
       
        exporter = DiagramExporter(self.gaphor_model_path)
        exporter.export(format=format, pattern=pattern, path=self.exported_images_path)


if __name__ == "__main__":
    # CONFIG_PATH = "C:\\Users\\Resonate Systems\\Documents\\repos\\rs24016-cdp-main\\src\\CollisionDetectionProcessor\\docs\\config.json"
    # with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
    #     config = json.load(config_file)
    runner = GaphorRunner(config="config.json") #using the config.json in lv doc tool 
    runner.extract_diagrams(format="svg", pattern=".*")
