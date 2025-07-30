# -*- coding: utf-8 -*-


import os
import re
import sys
from clasaua.lib.clasaua import Clasaua


def clasaua():
    print("Launcher clasaua function")
    arguments = sys.argv
    app_file_path = re.sub(r'(-script\.py|-script\.pyw|\.exe)?$', '', arguments[0])
    if len(arguments) > 1:
        file_path = arguments[1]
        if os.path.isfile(file_path):
            file_path = file_path
            app_path_folder = os.path.dirname(os.path.realpath(__file__))
            print("app_path_folder: {}".format(app_path_folder))        
            work_path_folder = os.getcwd()
            # check logos in work_path_folder
            images = (
                'logo_foot.png',
                'logo_left.png',
                'logo_right.png')
            images_in_work_path_folder = True
            for image in images:
                image_path = '{}{}{}'.format(work_path_folder, os.sep, image) 
                print("image_path: {}".format(image_path))
                if not os.path.isfile(image_path):
                    images_in_work_path_folder = False
            if images_in_work_path_folder:
                images_in_work_path_folder = work_path_folder
            print("work path folder: {}".format(work_path_folder))
            Clasaua(app_path_folder=app_path_folder, file_path=file_path, work_path_folder=images_in_work_path_folder)
        else:
            print("Clasifications file path not exists.")
    else:
        print("Please specify the ODS file with the classification.")


if __name__ == "__main__":
    print("Launcher main")
    sys.exit(clasaua())
