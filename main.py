"""
This is an DocumentCloud Add-On that,
when given a public Google Drive or Dropbox link containing EML/MSG files,
will convert them to PDFs and upload them to DocumentCloud
"""
import os 
import re
import subprocess
from documentcloud.addon import AddOn

class ConvertEmail(AddOn):
    """DocumentCloud Add-On that converts EML/MSG files to PDFs and uploads them to DocumentCloud"""
    
    def eml_to_pdf(fp, new_name=None, timeout=180):
	    converter_jar = 'email.jar'
	    if new_name:
		    new_fp = dirname(fp) + '/' + new_name
		    bash_cmd = ['bash', '-c', f"timeout {timeout} java -jar {converter_jar} -o '{new_fp}' ; :"]
	    else:
		    bash_cmd = ['bash', '-c', f"timeout {timeout} java -jar {converter_jar} '{fp}' ; :"]
	    conv_run = subprocess.run(bash_cmd, stderr=subprocess.PIPE)
	    print(conv_run.stderr)
	    pdf_fp = re.sub('.eml$', '.pdf', fp)    
	    return pdf_fp

    
    def main(self):
        #name = self.data.get("name", "world")

        self.set_message("Retrieving EML/MSG files...")
        self.set_message("Converting EML/MSG files to PDFs...")
        self.set_message("Uploading converted files to DocumentCloud...")


if __name__ == "__main__":
    ConvertEmail().main()
