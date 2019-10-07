# -*- coding: utf-8 -*-
"""
created on 21/02/2019 17:15
@author: fgiely
"""

from CoreNLG.DocumentConstructors import Datas, Document, TextClass


project_input = {"infos": {"project_name": "quickstart"}}


class MyDatas(Datas):

    """Class to store data with the additional information of the project name"""

    """
    A class witch inherits CoreNLG.Datas to store short acces to some datas.
    All attributes of this class are accessible to all class inheriting CoreNLG.TextClass
    """

    def __init__(self, json_in: dict):
        super(MyDatas, self).__init__(json_in)
        self.p_name = json_in["infos"]["project_name"]


class MyProject:
    def __init__(self, json_in):
        self.datas = MyDatas(json_in)
        self.document = Document(self.datas, lang="fr")
        self.intro = Intro(self.document)
        self.part_one = PartOne(self.document)


class Intro(TextClass):
    def __init__(self, document):
        self.section = document.new_section(html_elem_attr={"id": "intro"})
        super().__init__(self.section)
        self.text = "banana"
        self.text = self.nlg_tags("h1", "intro du projet")
        self.text = self.nlg_tags("h2", self.p_name)
        document.write_section(self.section)


class PartOne(TextClass):
    def __init__(self, document):
        self.section = document.new_section(html_elem="p")
        super().__init__(self.section)
        self.text = "Première partie.ce est"
        self.text = self.nlg_syn(["génial", "super"])
        self.text = "!jusque à les"
        document.write_section(self.section)


if __name__ == "__main__":
    p = MyProject(project_input)
    p.document.open_in_browser()

    print(p.document)
    print(p.intro.section)
