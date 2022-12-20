"""
This is an DocumentCloud Add-On that,
when given a public Google Drive or Dropbox link containing EML/MSG files,
will convert them to PDFs and upload them to DocumentCloud
"""
import os 
import re
import shutil
import subprocess
from documentcloud.addon import AddOn
from clouddl import grab

class ConvertEmail(AddOn):
	"""DocumentCloud Add-On that converts EML/MSG files to PDFs and uploads them to DocumentCloud"""
	def check_permissions(self):
		"""The user must be a verified journalist to upload a document"""
		self.set_message("Checking permissions...")
		user = self.client.users.get("me")
		if not user.verified_journalist:
			self.set_message(
				"You need to be verified to use this add-on. Please verify your "
				"account here: https://airtable.com/shrZrgdmuOwW0ZLPM"
			)
			sys.exit()
	def fetch_files(self, url):
		"""Fetch the files from either a cloud share link or any public URL"""
		self.set_message("Retrieving EML/MSG files...")
		os.makedirs(os.path.dirname("./out/"), exist_ok=True)
		downloaded = grab(url, "./out/")

	def eml_to_pdf(fp, new_name=None, timeout=180):
		converter_jar = 'email.jar'
		if new_name:
			new_fp = os.path.dirname(fp) + '/' + new_name
			bash_cmd = ['bash', '-c', f"timeout {timeout} java -jar {converter_jar} -o '{new_fp}' ; :"]
		else:
			bash_cmd = ['bash', '-c', f"timeout {timeout} java -jar {converter_jar} '{fp}' ; :"]
		conv_run = subprocess.run(bash_cmd, stderr=subprocess.PIPE)
		print(conv_run.stderr)
		pdf_fp = re.sub('.eml$', '.pdf', fp)    
		return pdf_fp

	def main(self):
		url = self.data["url"]
		self.check_permissions()
		self.fetch_files(url)
		
		successes = 0
		errors = 0
		for current_path, folders, files in os.walk("./out/"):
			for file_name in files:
				file_name = os.path.join(current_path, file_name)
				basename = os.path.basename(file_name)
				self.set_message("Attempting to convert EML/MSG files to PDFs...")
				try:
					result = self.eml_to_pdf(file_name)
				except RuntimeError:
					errors += 1
					continue
				self.set_message("Uploading converted file to DocumentCloud...")
				self.client.documents.upload(f"{basename}.pdf")
				successes += 1
			
		sfiles = "file" if successes == 1 else "files"
		efiles = "file" if errors == 1 else "files"
		self.set_message(f"Transcribed {successes} {sfiles}, skipped {errors} {efiles}")
		shutil.rmtree("./out/", ignore_errors=False, onerror=None)

if __name__ == "__main__":
	ConvertEmail().main()
