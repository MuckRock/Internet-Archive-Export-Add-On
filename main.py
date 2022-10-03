""" This program uses the internetarchive python library and DocumentCloud's addon system"""
import os.path
import os
import shutil
from documentcloud.addon import AddOn
from internetarchive import upload


class Archive(AddOn):
    """Based on DocumentCloud HelloWorld template Add-On."""

    def main(self):
        """
        At the present time all items are uploaded to Document Cloud's Internet Archive page,
        which can be found here: https://archive.org/details/@documentcloudupload
        If you fork the project and create your own repo secrets (IA_USER and IA_PASS),
        The code will upload to your Internet Archive account.
        The call to os.system() is to set up the IA.INI configuration file
        which is required to use the Internet Archive's Python Library.
        See https://archive.org/services/docs/api/internetarchive/quickstart.html
        """
        os.makedirs(os.path.dirname("./out/"), exist_ok=True)
        # pulls the project name Add-On UI or if run locally on CLI through --data.
        projectname = self.data.get("projectname")
        # pulls the item name from Add-On UI or if run locally on CLI through --data
        itemname = self.data.get("itemname")
        # Item names in the Internet archive cannot include spaces, so spaces -> dashes.
        itemname = itemname.replace(" ", "-")
        # DocumentCloud API call to get the project object.
        project = self.client.projects.get(id=None, title=projectname)
        # pulls the internet archive username secret(token) from the workflow environment.
        ia_user = os.environ["TOKEN"]
        # pulls the internet archive password secret(key) from the workflow environment.
        ia_pass = os.environ["KEY"]
        # sets up the config file to allow us to use the Archive Python library.
        cmd = "ia configure --username " + ia_user + " " + "--password " + ia_pass
        # runs the command in the shell to generate the configuration file.
        os.system(cmd)

        for document_id in project.document_ids:
            # retrieves an individual project using the DocumentCloud Python Wrapper get() method
            document = self.client.documents.get(document_id)
            # Saves the project document to ./out/ with the currect file path.
            title = document.title + ".pdf"
            save_path = "./out"
            full_path = os.path.join(save_path, title)
            with open(full_path, "wb") as file:
                file.write(document.pdf)
            # Uploads the file to the item in the Internet Archive.
            upload(itemname, files=full_path)
        # temporary  directory out is deleted after completion.
        shutil.rmtree("./out/", ignore_errors=False, onerror=None)


if __name__ == "__main__":
    Archive().main()
