""" This program uses the internetarchive python library and DocumentCloud's addon system"""
import os.path
import shutil
import time
from pathlib import Path

from internetarchive import upload
from documentcloud.addon import AddOn
from documentcloud.exceptions import APIError

FILECOIN_ID = 104


class Archive(AddOn):
    """Based on DocumentCloud HelloWorld template Add-On."""

    def tag_document(self, document, item_url, max_retries=5, retry_delay=60):
        """Set the ia_url data tag on a document via the narrow data endpoint,
        retrying on API errors. Returns True on success, False if retries are exhausted.
        """
        retries = 0
        while retries < max_retries:
            try:
                print(f"Tagging document {document.id}...")
                existing = document.data.get("ia_url", [])
                # remove any existing value, then set the new one (idempotent on re-run)
                self.client.patch(
                    f"documents/{document.id}/data/ia_url/",
                    json={"values": [item_url], "remove": existing},
                )
                self.client.patch(
                    f"documents/{document.id}/data/ia_url/",
                    json={"values": [item_url]},
                )
                print("Finished tagging document")
                return True
            except APIError as exc:
                print(f"Error tagging document {document.id}. {exc}. Retrying...")
                retries += 1
                time.sleep(retry_delay)
        print(f"Failed to tag document {document.id} after {max_retries} attempts.")
        self.set_message(
            "Failed to set the IA URL tag for a document. "
            "Email info@documentcloud.org to debug."
        )
        return False

    def main(self):
        """
        At the present time all items are uploaded to Document Cloud's Internet Archive page,
        which can be found here: https://archive.org/details/@documentcloudupload
        If you fork the project and create your own repo secrets (TOKEN and KEY for your
        IA-S3 access key and secret key), the code will upload to your Internet Archive
        account. You can retrieve your IA-S3 keys at https://archive.org/account/s3.php.
        See https://archive.org/developers/internetarchive/configuration.html
        """
        self.client.session.headers.update({'User-Agent': 'IA Export Add-On'})
        if not self.documents:
            self.set_message("Please select at least one document")
            return
        os.makedirs(os.path.dirname("./out/"), exist_ok=True)
        item_name = self.data["item_name"]
        # Item names in the Internet archive cannot include spaces, so spaces -> dashes.
        item_name = item_name.replace(" ", "-")
        # pulls the IA-S3 access key & secret key secrets from the workflow environment.
        ia_access = os.environ["TOKEN"]
        ia_secret = os.environ["KEY"]
        # write the config file for Internet Archive API access.
        config_path = Path.home() / ".config" / "internetarchive" / "ia.ini"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(f"[s3]\naccess = {ia_access}\nsecret = {ia_secret}\n")

        item_url = f"https://archive.org/details/{item_name}"
        doc_ids = []
        for document in self.get_documents():
            document_id = str(document.id)
            title = f'{document.title}-{document_id}.pdf'
            save_path = "./out"
            full_path = os.path.join(save_path, title)
            with open(full_path, "wb") as file:
                file.write(document.pdf)

            try:
                upload(item_name, files=full_path)
            except Exception as exc:  # upload failed — leave untagged so it's retried
                print(f"Upload failed for {document_id}: {exc}")
                self.set_message(f"Upload failed for {document_id}: {exc}")
                continue

            # upload succeeded — tag the item location
            self.tag_document(document, item_url)
            doc_ids.append(document_id)

        if self.data.get("filecoin") and doc_ids:
            self.client.post(
                "addon_runs/",
                json={"addon": FILECOIN_ID, "parameters": {}, "documents": doc_ids},
            )
        # temporary  directory out is deleted after completion.
        shutil.rmtree("./out/", ignore_errors=False, onerror=None)


if __name__ == "__main__":
    Archive().main()
