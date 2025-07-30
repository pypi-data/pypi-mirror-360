from typing import List, Union, Tuple

import numpy as np
from checkmarkandcross import image


def aufgabe1_1(cast: np.ndarray):
    return image(isinstance(cast, np.ndarray)
                 and np.shape(cast) == (3646, 3646)
                 and cast[200, 2802] == 2
                 and cast[400, 134] == 6
                 and cast[600, 203] == 2)


def aufgabe1_2(cast_names: List[str]):
    return image(isinstance(cast_names, list)
                 and len(cast_names) == 3646
                 and cast_names[129] == 'Alvy Moore'
                 and cast_names[687] == 'Clay Savage'
                 and cast_names[2765] == 'Paul Winchell')


def aufgabe2_1(max_value: float, max_indices: Union[np.ndarray, tuple]):
    return image(max_value == 57.
                 and ((
                              isinstance(max_indices, np.ndarray)
                              and max_indices.shape == (2, 2)
                              and (max_indices[0] == [1192, 1192]).all()
                      )
                      or (
                              isinstance(max_indices, tuple)
                              and len(max_indices) == 2
                              and len(max_indices[0]) == 2
                              and max_indices[0][0] == 1192
                              and max_indices[1][0] == 1192
                      ))
                 )


def aufgabe2_2(names: List[str]):
    return image(isinstance(names, list)
                 and len(names) == 2
                 and (
                         names[0].startswith('Frank W')
                         or names[1].startswith('Frank W')
                 ))


def aufgabe3_1(cast_wo_self: np.ndarray):
    return image(isinstance(cast_wo_self, np.ndarray)
                 and (cast_wo_self * np.eye(*cast_wo_self.shape) == np.zeros(cast_wo_self.shape)).all())


def aufgabe3_2(max_value: float, max_indices: np.ndarray):
    return image(max_value == 26.
                 and ((
                              isinstance(max_indices, np.ndarray)
                              and max_indices.shape == (2, 2)
                              and max_indices[0, 0] == 2510
                      )
                      or (
                              isinstance(max_indices, tuple)
                              and len(max_indices) == 2
                              and len(max_indices[0]) == 2
                              and max_indices[0][0] == 2510
                      ))
                 )


def aufgabe3_3(names: List[Tuple[str, str]]):
    return image(isinstance(names, list)
                 and len(names) == 2
                 and (
                         'cki' in names[0]
                         or 'cki' in names[1]
                 )
                 and (
                         'ry' in names[0]
                         or 'ry' in names[1]
                 ))
