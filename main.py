from documentcloud.addon import AddOn
from documentcloud import DocumentCloud
from internetarchive import upload
import os.path
import os
import shutil

class Archive(AddOn):
    def main(self):
        os.makedirs(os.path.dirname('./ia/'), exist_ok=True)
        pname = self.data.get('pname') 
        iname = self.data.get('iname')
        iname = iname.replace(' ', '-')
        p = self.client.projects.get(id=None, title=pname)
        
        for i in p.document_ids:
            d = self.client.documents.get(i)
            p = d.pdf
            t = d.title + ".pdf"
            save_path='./ia'
            full_path = os.path.join(save_path, t)
            with open(full_path, 'wb') as f:
                f.write(d.pdf)
            r = upload(iname, files = full_path)
        shutil.rmtree('./ia/', ignore_errors=False, onerror=None)
        

if __name__ == "__main__":
    Archive().main()
