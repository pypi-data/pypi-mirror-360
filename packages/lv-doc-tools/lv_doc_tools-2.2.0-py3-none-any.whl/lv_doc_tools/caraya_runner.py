
import os
from pathlib import Path
import glob
from lv_doc_tools.config_loader import Doc_Config_Loader
import sys
import subprocess

class Caraya_Runner:
    """
    Class to find and run Caraya tests based on a configuration file.
    """

    def __init__(self,config):
        """
        Constructor for the class

        Args:
            config (dict or Path): a dictionary with config or a path to the config file
        """
        # print(f"Config: {config}")
        self.config = Doc_Config_Loader(config)
        self.xml_dir = self.config.paths['test_xml']
        self.gcli_commands = []
        self.build_g_cli_commands()

    def cleanup_xml_folder(self):
        """
        Cleans up the test xml folder before running tests
        """
        print(f"Cleaning up xml folder: {self.xml_dir}")
        if self.xml_dir.exists():
            for item in self.xml_dir.iterdir():
                if item.is_file():
                    item.unlink()
        else:
            # Create the test xml folder if it doesn't exist
            self.xml_dir.mkdir(parents=True, exist_ok=True)


    def build_g_cli_commands(self):
        """
        Builds the commands to run the caraya xml parser
        """            
        #run tests for each defined test item vi/project etc
        if isinstance(self.config.tests, dict):
            for suitename,iTest_items in self.config.tests.items():
                # print(f"iTest_items: {iTest_items}")
                for iTestPath in iTest_items:
                    #if iTestPath is a directory, run the tests in that directory
                    if iTestPath.is_dir():
                        testFiles = [x for x in iTestPath.glob("*.vi")]
                        testFiles.sort()  # Sort to ensure consistent order
                    #if iTestPath is a file, run the tests in that file
                    else:
                        testFiles = [iTestPath]
                    for iTestFile in testFiles:
                        gcli_command = [
                            "g-cli", "--lv-ver", "2025",
                            self.config.paths['caraya'],
                            "--","-s",iTestFile,
                            "-x",self.config.paths['test_xml'].joinpath(f"{suitename}__{iTestFile.stem}.xml")
                        ]
                        self.gcli_commands.append(gcli_command)   
        else:
            raise ValueError("Config tests must be a dictionary of test suites.")                                                                                                                                                                                                                                                                                                                              


    def run_tests(self):
        """
        Runs the Caraya tests using self.gcli_commands 
        """
        self.cleanup_xml_folder()
                        
        for iCommand in self.gcli_commands:
            print(f"Running command: {iCommand}")
            if sys.platform == "win32":
                try:
                    result = subprocess.run(iCommand, check=True)
                    if result.returncode != 0:
                        print(f"Subprocess failed, with returncode: {result.returncode}. stdout: {result.stdout}\nstderr:{result.stderr}")
                    else:
                        print(f"Test Report for {str(iCommand[6])} generated successfully.")
                except Exception as e:
                    print(f"Error running tests: {str(iCommand[6])}. Error text: {repr(e)}")
            else:
                print("This script is designed to run on Windows with the Caraya CLI engine. Please run it on a Windows machine.")
                print('command to run: ' + ' '.join(iCommand))


def cli():
    """
    Command line interface for the Caraya_Parser
    """
    import argparse

    parser = argparse.ArgumentParser(description="Caraya Runner CLI")
    parser.add_argument("config", type=str, help="Path to the configuration file")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    test_runner = Caraya_Parser(config_path)
    test_runner.run_tests()


if __name__ == "__main__":
    """
    runs tests based on configuration file
    """
    cli()
