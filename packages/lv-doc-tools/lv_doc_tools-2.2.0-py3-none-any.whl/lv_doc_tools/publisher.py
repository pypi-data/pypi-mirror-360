
import os
from pathlib import Path
import glob
from lv_doc_tools.config_loader import Doc_Config_Loader
import sys
import subprocess
import json
import time
import datetime
from atlassian import Confluence

class Publisher:
    """
    Class to publish the final Html or pdf file to confluence.
    """

    def __init__(self,config):
        """
        Constructor for the class

        Args:
            config (dict or Path): a dictionary with config or a path to the config file
        """
        print(f"Config: {config}")
        self.config = Doc_Config_Loader(config)
        self.output_dir=self.config.paths['output']
        self.title=self.config.title
        self.confluence_dict = self.config.confluence

    def publish_to_confluence(self):
        """
        Push HTML output to confluence
        """

        confluence = Confluence(
                    url=self.confluence_dict["URL"],
                    username=self.confluence_dict["USERNAME"],
                    password=self.confluence_dict["API_TOKEN"])
        print("Authenticated Successfully")

        self.space_key = self.confluence_dict["SPACE_KEY"]
        self.page_title = self.confluence_dict["PAGE_TITLE"] 

        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if filename.endswith((".pdf", ".xlsx")):
                # pdf_file_path = os.path.join(self.output_dir, filename)
                    # Check if the Confluence page exists
                #Getting Metadata
                file_title=os.path.splitext(filename)[0]
                creation_time=os.path.getctime(file_path)
                modified_time=os.path.getmtime(file_path)
                date_created=datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
                date_modified=datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")

                metadata_table = f"""
                <table>
                    <tbody>
                        <tr><th>Title</th><td>{file_title}</td></tr>
                        <tr><th>Date Created</th><td>{date_created}</td></tr>
                        <tr><th>Date modified</th><td>{date_modified}</td></tr>
                    </tbody>
                </table>
                <p>The PDF document is attached to this page.</p>
                """
                page_id = None
                if confluence.page_exists(self.space_key, self.page_title):
                    existing_page = confluence.get_page_by_title(
                        self.space_key, self.page_title
                    )
                    if existing_page:
                        page_id = existing_page["id"]
                        confluence.update_page(
                            page_id=page_id,
                            title=self.page_title,
                            body=metadata_table,
                            representation="storage"
                        )
                else:
                    # Create a new page and get its ID
                    created_page = confluence.create_page(
                        space=self.space_key,
                        title=self.page_title,
                        body=metadata_table,
                        representation="storage"
                    )
                    page_id = created_page["id"]
                    print("New page created.")
                content_type = "application/pdf" if filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                upload_name = self.title if filename.endswith(".pdf") else f"{self.title}.xlsx"

                response = confluence.attach_file(
                    filename=file_path,
                    name=upload_name,
                    content_type=content_type,
                    page_id=page_id,
                )
                print(f"{filename} attached and updated to Confluence successfully.")
            
      


if __name__ == "__main__":
    """
   
    """
    CONFIG_PATH = "C:\\Users\\Resonate Systems\\Documents\\repos\\rs24016-hitachi-testing\\docs\\config.json"
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    mypublisher= Publisher(config)
    mypublisher.publish_to_confluence()
