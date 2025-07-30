# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

import json
import os
from pathlib import Path
from zipfile import is_zipfile, ZipFile
try:
    from .story_data import StoryFilesData
except:
    from story_data import StoryFilesData

"""
    3 Files:
    - stories
    - choices
    - scriptures

    These files are json formats:
    Stories - 
    {"stories": {
            "begin": "......",
            "first": {
                "A": ".....",
                "B": ".....",
                "C": ".....",
            },
            "second": {
                "A": ".....",
                "B": ".....",
                "C": ".....",
            }
        }
    }

    Choices -
    {"choices":
        { 
            "first": {
                "A": ".....",
                "B": ".....",
                "C": ".....",
            },
            "second": {
                "A": ".....",
                "B": ".....",
                "C": ".....",
            }
        }
    }

    Scriptures -
    {"scriptures":
        {
            "A": ".....",
            "B": ".....",
        }
    }
""" 

class StoryFilesArchive(StoryFilesData):
    """Archiving files of Stories, with Json format"""

    def __init__(self, path: str, *args):
        if args:
            super().__init__(*args)
        else:
            super().__init__(None, None, None)
        self.path = Path(path)
        

    def creating_files(self) -> list[str]:
        """Creating json files for each story"""

        files = {"stories": self.stories, "choices": self.choices, "scriptures": self.scriptures}
        list_files = []
        for k, v in files.items():
            pth = self.path.joinpath(f"{k}.json")
            if not pth.exists() and v:
                with open(pth, "w") as story:
                    json.dump(v, story)
                list_files.append(pth)
            del pth
        return list_files
    
    def deleting_files(self):
        """deleting json files"""

        files = ["stories", "choices", "scriptures"]
        for file in files:
            pth = self.path.joinpath(f"{file}.json")
            if pth.exists():
                os.remove(pth)
            del pth
        del files
    
    def archiving_zip(self, name: str):
        """Archiving story to a zip file for loading or deleting all json files"""

        if files := self.creating_files():
            if not is_zipfile(self.path.joinpath(f"{name}.zip")):        
                with ZipFile(self.path.joinpath(f"{name}.zip"), "x") as zipped: 
                    for file in files:
                        zipped.write(file.name)                
            else:
                with ZipFile(self.path.joinpath(f"{name}.zip"), "w") as zipped: 
                    for file in files:
                        zipped.write(file.name)
            self.deleting_files()

    def unarchived_zip(self, name: str):
        """Extracting file from a zip file"""
        
        if is_zipfile(self.path.joinpath(f"{name}.zip")):
            with ZipFile(self.path.joinpath(f"{name}.zip")) as zipped:
                for file in zipped.filelist:
                    zipped.extract(file)
    
    def delete_zipfile(self, name: str):
        """Deleting a zip file"""

        if is_zipfile(self.path.joinpath(f"{name}.zip")):
            os.remove(self.path.joinpath(f"{name}.zip"))