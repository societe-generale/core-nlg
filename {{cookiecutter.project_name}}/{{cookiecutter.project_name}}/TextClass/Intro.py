# -*- coding: utf-8 -*-

from CoreNLG.DocumentConstructors import TextClass


class Intro(TextClass):
    def __init__(self, section):
        super().__init__(section)

        introduction = self.free_text(
            self.title(),
            self.intro()
        )

        self.text = self.nlg_tags('div', id='introduction_id', text=introduction)

    def title(self):
        return self.nlg_tags('h2', self.project_name)

    def intro(self):
        return 'Hello world !'
