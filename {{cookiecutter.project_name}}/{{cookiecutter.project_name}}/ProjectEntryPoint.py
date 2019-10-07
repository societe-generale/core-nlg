# -*- coding: utf-8 -*-
import json
from CoreNLG.DocumentConstructors import Document

from {{cookiecutter.project_name}}.Datas.MyDatas import MyDatas
from {{cookiecutter.project_name}}.TextClass.Intro import Intro
from {{cookiecutter.project_name}}.TextClass.Content import Content


class {{cookiecutter.project_name|capitalize}}:
    def __init__(self, _json):
        processed_json = self.pre_processing(_json)

        datas = MyDatas(processed_json)
        self.document = Document(datas)

        my_section = self.document.new_section()

        Intro(my_section)
        Content(my_section)

        self.document.write()

        self.result = self.post_processing()

    def pre_processing(self, _json):
        return _json

    def post_processing(self):
        return str(self.document)


if __name__ == "__main__":
    with open("../inputs/test.json") as input_file:
        engine = {{cookiecutter.project_name|capitalize}}(json.load(input_file))

    engine.document.open_in_browser()
    print(engine.post_processing())
