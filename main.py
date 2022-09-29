from documentcloud.addon import AddOn
from documentcloud import DocumentCloud
from internetarchive import upload
import os.path
import os
import shutil

class Archive(AddOn):
    def main(self):
        os.makedirs(os.path.dirname('./out/'), exist_ok=True)
        pname = self.data.get('pname') 
        iname = self.data.get('iname')
        iname = iname.replace(' ', '-')
        p = self.client.projects.get(id=None, title=pname)
        ia_user=os.environ["IA_USER"]
        # ia_pass=os.environ["IA_PASS"]
        # cmd = 'ia configure --username ' + ia_user + ' ' + '--password ' + ia_pass
        # os.system(cmd)
        
        for i in p.document_ids:
            d = self.client.documents.get(i)
            p = d.pdf
            t = d.title + ".pdf"
            save_path='./out'
            full_path = os.path.join(save_path, t)
            with open(full_path, 'wb') as f:
                f.write(d.pdf)
            r = upload(iname, files = full_path)
        shutil.rmtree('./out/', ignore_errors=False, onerror=None)

if __name__ == "__main__":
    Archive().main()
