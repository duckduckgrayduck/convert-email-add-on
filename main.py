"""
This is an DocumentCloud Add-On that,
when given a public Google Drive or Dropbox link containing EML/MSG files,
will convert them to PDFs and upload them to DocumentCloud
"""
import os 
import shutil
import requests
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
		os.makedirs(os.path.dirname("./attach/"), exist_ok=True)
		downloaded = grab(url, "./out/")

	def eml_to_pdf(self, fp):
		url= 'https://github.com/nickrussler/email-to-pdf-converter/releases/download/2.5.3/emailconverter-2.5.3-all.jar'
		resp = requests.get(url, timeout=10)
		with open('email.jar', 'wb') as file:
			file.write(resp.content)
		if self.data["attachments"]:
			bash_cmd = f"java -jar email.jar -a {fp}; mv ./out/EMLs/*attachments* attach;"
		else:
			bash_cmd = f"java -jar email.jar {fp}"
		conv_run = subprocess.call(bash_cmd, shell=True)

	def main(self):
		url = self.data["url"]
		#extract_attachments = self.data["attachments"]
		self.check_permissions()
		self.fetch_files(url)
		
		successes = 0
		errors = 0
		for current_path, folders, files in os.walk("./out/"):
			for file_name in files:
				file_name = os.path.join(current_path, file_name)
				basename = os.path.basename(file_name)
				self.set_message("Attempting to convert EML/MSG files to PDFs...")
				abs_path = os.path.abspath(file_name)
				try:
					result = self.eml_to_pdf(abs_path)
				except RuntimeError:
					errors += 1
					continue
				else: 
					self.set_message("Uploading converted file to DocumentCloud...")
					file_name_no_ext = os.path.splitext(abs_path)[0]
					self.client.documents.upload(f"{file_name_no_ext}.pdf")
					successes += 1
		
		if self.data["attachments"]:
			subprocess.call("zip -r attachments.zip attach", shell=True)
			self.upload_file(open("attachments.zip"))

		sfiles = "file" if successes == 1 else "files"
		efiles = "file" if errors == 1 else "files"
		self.set_message(f"Converted {successes} {sfiles}, skipped {errors} {efiles}")
		shutil.rmtree("./out", ignore_errors=False, onerror=None)
		shutil.rmtree("./attach", ignore_errors=False, onerror=None)

if __name__ == "__main__":
	ConvertEmail().main()
