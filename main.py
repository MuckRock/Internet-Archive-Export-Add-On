from documentcloud.addon import AddOn
from documentcloud import DocumentCloud
from internetarchive import upload
import os.path
import os
import shutil

""" This program creates a temporary directory(out) and then gets a project name and an item name 
    for an Internet Archive item from the DocumentCloud add-on prompt. 
    See https://archive.org/services/docs/api/items.html for more on items. 
    It then finds the DocumentCloud project with the matching name 
    and uploads each document in the project to the corresponding Internet Archive item. 
    At the present time all items are uploaded to Document Cloud's Internet Archive page which can be found here: 
    https://archive.org/details/@documentcloudupload 
    If you fork the project and create your own repository secrets (they must be named IA_PASS and IA_USER) 
    The code will upload to your Internet Archive account. 
    The call to os.system() is to set up the IA.INI configuration file 
    which is required to use the Internet Archive's Python Library. 
    See https://archive.org/services/docs/api/internetarchive/quickstart.html to learn more about this library. 
    """


class Archive(AddOn):
    def main(self):
        os.makedirs(os.path.dirname("./out/"), exist_ok=True)
        # pulls the project name from the DocumentCloud UI Add-On or if run locally on CLI through --data.
        projectname = self.data.get("projectname")
        # pulls the item name from the DocumentCloud Add-On or if run locally on CLI through --data
        itemname = self.data.get("itemname")
        # Item names in the Internet archive cannot include spaces, so if a user submits a name with spaces, it will be replaced with dashes.
        itemname = itemname.replace(" ", "-")
        # DocumentCloud API call to get the project object with the title that matches the project we pulled earlier.
        project = self.client.projects.get(id=None, title=projectname)
        # pulls the internet archive username secret from the environment, it is stored under token in the Add-On workflow.
        ia_user = os.environ["TOKEN"]
        # pulls the internet archive password secret from the environment, it is stored under key in the Add-On  workflow.
        ia_pass = os.environ["KEY"]
        # sets up the command to configure the IA.INI file to run the Internet Archive Python library.
        cmd = "ia configure --username " + ia_user + " " + "--password " + ia_pass
        # runs the command in the shell to generate the configuration file.
        os.system(cmd)

        for document_id in project.document_ids:
            # retrieves an individual project using the DocumentCloud Python Wrapper get() method
            document = self.client.documents.get(document_id)
            # retrieves the pdf version of the document.
            pdf = document.pdf
            # the next three lines of code saves the project document to ./out/ with the currect file path.
            title = document.title + ".pdf"
            save_path = "./out"
            full_path = os.path.join(save_path, title)
            with open(full_path, "wb") as f:
                f.write(document.pdf)
            # Uploads the file to the item in the Internet Archive.
            request = upload(itemname, files=full_path)
        # temporary  directory is deleted after completion. Since it is not empty, we must use .rmtree()
        shutil.rmtree("./out/", ignore_errors=False, onerror=None)


if __name__ == "__main__":
    Archive().main()
