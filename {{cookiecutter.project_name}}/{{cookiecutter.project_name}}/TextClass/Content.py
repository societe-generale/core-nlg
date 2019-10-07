# -*- coding: utf-8 -*-

from CoreNLG.DocumentConstructors import TextClass


class Content(TextClass):
    def __init__(self, section):
        super().__init__(section)

        content = self.free_text(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit,",
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        )

        self.text = self.nlg_tags('div', id='content_id', text=content)
