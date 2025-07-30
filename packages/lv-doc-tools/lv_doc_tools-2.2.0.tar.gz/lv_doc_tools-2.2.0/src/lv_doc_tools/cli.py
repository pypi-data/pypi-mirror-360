import json
import argparse
from lv_doc_tools.generator import Doc_Generator
from lv_doc_tools.caraya_runner import Caraya_Runner
from lv_doc_tools.caraya_parser import Caraya_Parser
from lv_doc_tools.publisher import Publisher
from lv_doc_tools.cleaner import Cleaner

def main():
  
    parser = argparse.ArgumentParser(
        description="Generate documentation for LabView projects using lv_doc_tools."
    )
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="Path to the configuration JSON file.",
    )

    parser.add_argument(
        "--to-confluence",
        action="store_true",
        help="If set, publish generated files to Confluence.",
    )

    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="If set,the cleaner will not remove the files and folders from output folder.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging purposes.",
    )


    args = parser.parse_args()


    try:
        with open(args.config, "r", encoding="utf-8") as fh:
            config = json.load(fh)
            if args.verbose:
                print(f"Loaded configuration: {config}")
            # Run tests
            mycaraya=Caraya_Runner(config)
            mycaraya.run_tests()

            mycarayaparser=Caraya_Parser(config)
            mycarayaparser.process_xml_files()

            
            # Generate documentation
            dg = Doc_Generator(config)
            dg.build_docs()
           
            print("Documentation built successfully!")
            if args.to_confluence:
                if args.verbose:
                    print("Publishing to Confluence...")
                mypublisher=Publisher(config)
                mypublisher.publish_to_confluence()

            if not args.no_clean:
                mycleaner=Cleaner(config)
                mycleaner.clean_output_dir()
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON in '{args.config}'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()