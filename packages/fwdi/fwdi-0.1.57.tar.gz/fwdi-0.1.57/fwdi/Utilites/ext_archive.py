import shutil
import zipfile
import os
from example.Utilites.ext_path import ExtPath
from example.Utilites.file_tools import FileTools
from fwdi.Utilites.ext_file import ExtFile

class ExtArchive():

    @staticmethod
    def zip_directory(directory_path, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), 
                                os.path.relpath(os.path.join(root, file), 
                                                os.path.join(directory_path, '..')))
            return zip_path
        except FileNotFoundError:
            print('ERROR: The file you are trying to zip does not exist.')
            return None
        except RuntimeError as e:
            print('ERROR: An unexpected error occurred:', str(e))
            return None            
        except zipfile.LargeZipFile:
            print('ERROR: The file is too large to be compressed.')        
            return None            

    @staticmethod
    def folder_to_zip(name:str, catalog_path:str)->str:
        temp_folder:str = os.path.abspath(ExtPath.get_tmp_folder())
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        try:
            archive_path = ExtArchive.zip_directory(catalog_path, f"{temp_folder}/{name}.zip") # shutil.make_archive(name, "gztar", catalog_path)

            folder_bytes:str = FileTools.encode_file_bytes_to_str(archive_path)

            if not ExtFile.delete(archive_path):
                raise Exception(f"Error delete temp archive file: {archive_path}")
            else:
                print(f"Deleted temp archive file: {archive_path}")

            return folder_bytes
        except Exception as ex:
            print(f"ERROR: {ex}")

    @staticmethod
    def zip_to_folder(zip_data:str, folder_path:str)->bool:
        try:
            with zipfile.ZipFile(zip_data, 'r') as zf:
                zf.extractall(folder_path)
            
            return True
        except Exception as ex:
            print(f"ERROR: {ex}")
            return False