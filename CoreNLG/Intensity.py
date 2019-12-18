# -*- coding: utf-8 -*-
"""
created on 09/12/2019 16:17
@author: fgiely
"""


class Intensity:
    # Todo : ned to be developed :)
    @staticmethod
    def intensity(num, intensity_def):
        print(intensity_def)
        for i, thresh in enumerate(intensity_def["threshold"]):
            if num < thresh:
                return intensity_def["intensity"][i]
        return intensity_def["intensity"][-1]


def intensity(num, intensity_def):
    return Intensity().intensity(num, intensity_def)
