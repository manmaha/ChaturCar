''' Upload all npy files from a given directory to a folder with same name in GDrive
    If folder does not exist in GDrive, create it!
'''
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import glob
import argparse
import os

def GDriveUpload(dirname,extn):

  #Authorize GDrive
  gauth = GoogleAuth()
  gauth.LocalWebserverAuth()
  drive = GoogleDrive(gauth)

  #Now Create Folder in GDrive
  folder_metadata = {
    'title' : dirname,
    # The mimetype defines this new file as a folder, so don't change this.
    'mimeType' : 'application/vnd.google-apps.folder'
  }
  folder = drive.CreateFile(folder_metadata)
  folder.Upload()

  # Get folder info and print to screen.
  folder_title = folder['title']
  folder_id = folder['id']
  print('title: %s, id: %s' % (folder_title, folder_id))
  # Now write all the files in dirname into folder
  os.chdir(dirname)
  for file in glob.glob('*.'+extn):
    f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}],"title":file})
#    print(file, f['title'])
    # Make sure to add the path to the file to upload below.
    f.SetContentFile(file)
    f.Upload()



def main():
    parser = argparse.ArgumentParser(description='Upload to GDrive')
    parser.add_argument('--folder', default='Examples1')
    parser.add_argument('--extn', default='npy')

    args = parser.parse_args()
    GDriveUpload(args.folder,args.extn)


if __name__=="__main__":
        main()
