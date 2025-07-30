# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

import json
import os
from pathlib import Path
try:
    from .story_archive import StoryFilesArchive
except:
    from story_archive import StoryFilesArchive


class StoryFilesLoads(StoryFilesArchive):
    """Story loader"""
    
    def _folder_files(self, name: str) -> None:
        """Unarchived zipfile to a folder"""
        
        pth = self.path.joinpath(name)
        if not pth.exists():
            self.unarchived_zip(name)
            pth.mkdir()
            files = ["stories", "choices", "scriptures"]
            for file in files:
                p = self.path.joinpath(f"{file}.json")
                p.rename(pth.joinpath(p.name))
                del p
            del files
        del pth

    def data_extract(self, name: str) -> list:
        """Extracted data individually to a list"""

        self._folder_files(name)
        datas = []
        files = ["stories", "choices", "scriptures"]
        for file in files:
            p = self.path.joinpath(name, f"{file}.json")
            with open(p) as d:
                datas.append(json.load(d))
            os.remove(p)
        os.rmdir(self.path.joinpath(name))
        del files
        return datas
    

if __name__ == "__main__":

    path = Path(__file__).parent
    #os.chdir(path=path)
    # data = [{"Stories": "..."}, {"choices": "..."}, {"scriptures": "..."}]
    # story = StoryFilesArchive(path, *data)
    # story.archiving_zip("test")
    # story.unarchived_zip("test")
    # story.deleting_files()

    # loadstory = StoryFilesArchive(path)
    # loadstory.unarchived_zip("test")
    # loadstory.deleting_files()
    # StoryFilesArchive(path).deleting_files()
    #print(*StoryFilesLoads(path).data_extract("test"))