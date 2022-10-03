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
        item_name = self.data["item_name"]
        # Item names in the Internet archive cannot include spaces, so spaces -> dashes.
        item_name = item_name.replace(" ", "-")
        # DocumentCloud API call to get the project object.
        # pulls the internet archive username & password secrets from the workflow environment.
        ia_user = os.environ["TOKEN"]
        ia_pass = os.environ["KEY"]
        # sets up the config file to allow us to use the Archive Python library.
        cmd = f'ia configure --username {ia_user} --password  {ia_pass}'
        # runs the command in the shell to generate the configuration file.
        os.system(cmd)

        for document in self.get_documents():
            title = document.title
            save_path = "./out"
            full_path = os.path.join(save_path, title)
            with open(full_path, "wb") as file:
                file.write(document.pdf)
            # Uploads the file to the item in the Internet Archive.
            upload(item_name, files=full_path)
        # temporary  directory out is deleted after completion.
        shutil.rmtree("./out/", ignore_errors=False, onerror=None)


if __name__ == "__main__":
    Archive().main()
