""" This program uses the internetarchive python library and DocumentCloud's addon system"""
import os.path
import subprocess
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
        The subprocess.call() runs the Internat Archive configuration command. 
        See https://archive.org/services/docs/api/internetarchive/quickstart.html
        """
        os.makedirs(os.path.dirname("./out/"), exist_ok=True)
        item_name = self.data["item_name"]
        # Item names in the Internet archive cannot include spaces, so spaces -> dashes.
        item_name = item_name.replace(" ", "-")
        # pulls the internet archive username & password secrets from the workflow environment.
        ia_user = os.environ["TOKEN"]
        ia_pass = os.environ["KEY"]
        # cmd to set up the config file for Internet Archive API access.
        cmd = f'ia configure --username {ia_user} --password  {ia_pass}'
        subprocess.call(cmd, shell=True)

        for document in self.get_documents():
            title = f'{document.title}.pdf'
            save_path = "./out"
            full_path = os.path.join(save_path, title)
            with open(full_path, "wb") as file:
                file.write(document.pdf)
            # Append the document ID to the item name to guarantee some uniqueness for item name. 
            document_id = str(document.id)
            item_name = f'{item_name} {document_id}'
            upload(item_name, files=full_path)
        # temporary  directory out is deleted after completion.
        shutil.rmtree("./out/", ignore_errors=False, onerror=None)


if __name__ == "__main__":
    Archive().main()
