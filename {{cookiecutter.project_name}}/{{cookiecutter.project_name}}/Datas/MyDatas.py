# -*- coding: utf-8 -*-

from CoreNLG.DocumentConstructors import Datas


class MyDatas(Datas):
    def __init__(self, json_in: dict):
        super().__init__(json_in)

        self.project_name = json_in['infos']['project_name']