"""
This is an DocumentCloud Add-On that,
when given a public Google Drive or Dropbox link containing EML/MSG files,
will convert them to PDFs and upload them to DocumentCloud
"""
from documentcloud.addon import AddOn
class ConvertEmail(AddOn):
    """DocumentCloud Add-On that converts EML/MSG files to PDFs and uploads them to DocumentCloud"""

    def main(self):
        #name = self.data.get("name", "world")

        self.set_message("Retrieving EML/MSG files...")
        self.set_message("Converting EML/MSG files to PDFs...")
        self.set_message("Uploading converted files to DocumentCloud...")


if __name__ == "__main__":
    ConvertEmail().main()
