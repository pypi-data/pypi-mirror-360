# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)


class StoryFilesData:

    def __init__(self, stories: dict[str, str], choices: dict[str, str], scriptures: dict[str, str]):
        self.stories = stories
        self.choices = choices
        self.scriptures = scriptures