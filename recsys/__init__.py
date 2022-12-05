#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Recommender Systems: Towards Deep Learning State-of-the-Art                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /recsys/__init__.py                                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/Recommender-Systems                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday November 13th 2022 05:00:30 pm                                               #
# Modified   : Sunday December 4th 2022 04:12:00 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #


# ------------------------------------------------------------------------------------------------ #
#                                    REPRODUCIBILITY                                               #
# ------------------------------------------------------------------------------------------------ #
RANDOM_STATE = 55
# ------------------------------------------------------------------------------------------------ #
#                                    TRAIN/TEST SPLIT                                              #
# ------------------------------------------------------------------------------------------------ #
TRAIN_PROPORTION = 0.8
# ------------------------------------------------------------------------------------------------ #
#                                      DATA TYPES                                                  #
# ------------------------------------------------------------------------------------------------ #
IMMUTABLE_TYPES: tuple = (str, int, float, bool, type(None))
SEQUENCE_TYPES: tuple = (list, tuple)
