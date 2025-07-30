# -*- coding: utf-8 -*-
"""
    @Author : PKing
    @E-mail :
    @Date   : 2024-05-23 11:24:37
    @Brief  : Series是一维数据结构，DataFrame二维表格结构，由多个Series组成（每列是一个Series）
"""
import os

import cv2
import numpy as np
from tqdm import tqdm
from pybaseutils import file_utils, image_utils, numpy_utils, pandas_utils, json_utils, text_utils
from pybaseutils.cvutils import corner_utils
from pybaseutils.dataloader import parser_labelme
from pybaseutils.converter import build_labelme
from scipy.spatial.distance import cdist
import hashlib
import pandas as pd
import nltk
from rich import print_json
import inspect
from pybaseutils import log
import asyncio

if __name__ == "__main__":
    pass
