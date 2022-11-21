#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Recommender Systems: Towards Deep Learning State-of-the-Art                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /operators.py                                                                       #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/Recommender-Systems                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday November 17th 2022 02:51:27 am                                             #
# Modified   : Sunday November 20th 2022 09:15:13 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
import os
from typing import Any, Union, List, Dict
import numpy as np
from numpy.random import default_rng
import pandas as pd
from abc import ABC, abstractmethod
import logging
import shlex
import subprocess
from zipfile import ZipFile

from recsys.core.services.profiler import profiler
from recsys.core.workflow.pipeline import Context
from recsys.core.dal.dataset import DatasetParams, Dataset
from recsys.core.dal.repo import repository

# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #


class Operator(ABC):
    """Abstract base class for pipeline operators.

    Note: All operator parameters in kwargs are added to the class as attributes.

    Args:
        name (str): The name for the operator that distinguishes it in the pipeline.
        description (str): A description for the operator instance. Optional
    """

    def __init__(self, **kwargs) -> None:
        self.name = None
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.name:
            self.name = self.__class__.__name__.lower()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}\n\tAttributes: {self.__dict__.items()}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\tAttributes: {self.__dict__.items()}"

    @profiler
    @abstractmethod
    def execute(self, data: pd.DataFrame = None, context: Context = None, **kwargs) -> Any:
        pass


# ------------------------------------------------------------------------------------------------ #
class DatasetOperator(ABC):
    """Base class for operators that interact with Dataset objects in the Dataset Repository.

    Input dataset parameters are queried by the repository decorator and the input dataset(s) are
    injected into the instance through the property setter. W.r.t the instance parameters,
    they are added to the class as attributes using setattr. Yeah, I know. Just got tired
    of typing get('param', None) from some parameters dictionary.

    Args:
        name (str): The name for the operator that distinguishes it in the pipeline.
        description (str): A description for the operator instance. Optional
        input_dataset_params (Union[DatasetParams], List[DatasetParams]) DatasetParams or a list
            thereof.
        output_dataset_params (Union[DatasetParams], List[DatasetParams]) DatasetParams or a list
            thereof.

    Attributes:
        input_dataset (Union[Dataset], List[Dataset]). The input dataset is injected by the
            repository decorator.

    Returns: Output Dataset Object
    """

    def __init__(self, *args, **kwargs) -> None:
        self.name = None

        self.input_data = None
        self.output_data = None

        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.name:
            self.name = self.__class__.__name__.lower()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}\n\tAttributes: {self.__dict__.items()}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\tAttributes: {self.__dict__.items()}"

    @property
    def input_data(self) -> Union[Dataset, Dict[str, Dataset], List[Dataset]]:
        return self._input_data

    @input_data.setter
    def input_data(self, input_data: Union[Dataset, Dict[str, Dataset], List[Dataset]]) -> None:
        self._input_data = input_data

    @profiler
    @repository
    @abstractmethod
    def execute(self, context: Context, **kwargs) -> Any:
        pass


# ------------------------------------------------------------------------------------------------ #
#                                     KAGGLE DOWNLOADER                                            #
# ------------------------------------------------------------------------------------------------ #


class KaggleDownloader(Operator):
    """Downloads Dataset from Kaggle using the Kaggle API
    Args:
        kaggle_filepath (str): The filepath for the Kaggle dataset
        destination (str): The folder to which the data will be downloaded.
    """

    def __init__(
        self,
        kaggle_filepath: str,
        destination: str,
        force: bool = False,
    ) -> None:
        name = self.__class__.__name__.lower()
        super().__init__(
            name=name,
            kaggle_filepath=kaggle_filepath,
            destination=destination,
            force=force,
        )

        self.command = (
            "kaggle datasets download" + " -d " + self.kaggle_filepath + " -p " + self.destination
        )

    def execute(self, *args, **kwargs) -> None:
        """Downloads compressed data via an API using bash"""
        os.makedirs(self.destination, exist_ok=True)
        if self._proceed():
            subprocess.run(shlex.split(self.command), check=True, text=True, shell=False)

    def _proceed(self) -> bool:
        if self.force:
            return True

        else:
            kaggle_filename = os.path.basename(self.kaggle_filepath) + ".zip"
            if os.path.exists(os.path.join(self.destination, kaggle_filename)):
                logger.info("Download skipped as {} already exists.".format(kaggle_filename))
                return False
            else:
                return True


# ------------------------------------------------------------------------------------------------ #
#                                     DEZIPPER - EXTRACT ZIPFILE                                   #
# ------------------------------------------------------------------------------------------------ #


class DeZipper(Operator):
    """Unzipps a ZipFile archive

    Args:
        zipfilepath (str): The path to the Zipfile to be extracted.
        destination (str): The directory into which the zipfiles shall be extracted
        members (list): Optional, list of members to be extracted
        force (bool): If True, unzip will overwrite existing file(s) if present.
    """

    def __init__(
        self,
        zipfilepath: str,
        destination: str,
        members: list = None,
        force: bool = False,
    ) -> None:
        name = self.__class__.__name__.lower()
        super().__init__(
            name=name,
            zipfilepath=zipfilepath,
            destination=destination,
            members=members,
            force=force,
        )

    def execute(self, *args, **kwargs) -> None:
        os.makedirs(self.destination, exist_ok=True)

        if self._proceed():
            with ZipFile(self.zipfilepath, "r") as zipobj:
                zipobj.extractall(path=self.destination, members=self.members)

    def _proceed(self) -> bool:
        if self.force:
            return True
        elif os.path.exists(os.path.join(self.destination, self.members[0])):
            zipfilename = os.path.basename(self.zipfilepath)
            logger.info("DeZip skipped as {} already exists.".format(zipfilename))
            return False
        else:
            return True


# ------------------------------------------------------------------------------------------------ #
#                                          PICKLER                                                 #
# ------------------------------------------------------------------------------------------------ #


class Pickler(Operator):
    """Converts a file to pickle format and optionally removes the original file.

    Args:
        infilepath (str): Path to file being converted
        outfilepath (str): Path to the converted file
        infile_format(str): The format of the input file
        infile_params (dict): Optional. Dictionary containing additional keyword arguments for reading the infile.
        usecols (list): List of columns to select.
        outfile_params (dict): Optional. Dictionary containing additional keyword arguments for writing the outfile.
        force (bool): If True, overwrite existing file if it exists.
        kwargs (dict): Additional keyword arguments to be passed to io object.
    """

    def __init__(
        self,
        infilepath: str,
        outfilepath: str,
        infile_format: str = "csv",
        usecols: list = [],
        index_col: bool = False,
        encoding: str = "utf-8",
        low_memory: bool = False,
        force: bool = False,
    ) -> None:
        super().__init__(
            infilepath=infilepath,
            outfilepath=outfilepath,
            infile_format=infile_format,
            usecols=usecols,
            index_col=index_col,
            encoding=encoding,
            low_memory=low_memory,
            force=force,
        )

    def execute(self, context: Context, *args, **kwargs) -> None:
        """Executes the operation

        Args:
            context (Context): Context object containing the name
                and description of Pipeline, and the io object as well.
        """
        if self._proceed():
            io = context.io
            data = io.read(
                filepath=self.infilepath,
                usecols=self.usecols,
                index_col=self.index_col,
                low_memory=self.low_memory,
                encoding=self.encoding,
            )
            os.makedirs(os.path.dirname(self.outfilepath), exist_ok=True)
            io.write(self.outfilepath, data)

    def _proceed(self) -> bool:
        if self.force:
            return True
        elif os.path.exists(self.outfilepath):
            outfilename = os.path.basename(self.outfilepath)
            logger.info("Pickler skipped as {} already exists.".format(outfilename))
            return False
        else:
            return True


# ------------------------------------------------------------------------------------------------ #
#                                     CREATE DATASET                                               #
# ------------------------------------------------------------------------------------------------ #


class CreateDataset(DatasetOperator):
    """Reads a DataFrame, creates a Dataset and commits it to the repository.

    Args:
        name (str): The name of the Dataset
        description (str): The description for the Dataset.
        infilepath (str): Path to the input file
        dataset_out_po (dict): Dictionary of Dataset parameters, including:
            - name (str): Name of the Dataset object
            - description (str): Brief description for the object.
            - env (str): One of 'dev', 'prod', or 'test'
            - stage (str): One of 'raw', 'interim', or 'cooked'
            - version (int): Version. Default = 1
            - version_control (bool): If True, saving an existing document will
                not throw an exception. Rather, the version will be bumped,
                and the id and filepath will be changed accordingly.

    Returns Dataset
    """

    def __init__(
        self, name: str, infilepath: str, dataset_out_po: dict, description: str = None
    ) -> None:
        super().__init__(
            self,
            name=name,
            description=description,
            infilepath=infilepath,
            dataset_out_po=dataset_out_po,
        )

    @repository
    def execute(self, context: Context = None, *args, **kwargs) -> Dict[str, Dataset]:
        """Creates the dataset."""
        io = context.io
        data = io.read(self.infilepath)
        dataset = Dataset(
            name=self.dataset_out_po["name"],
            description=self.dataset_out_po["description"],
            stage=self.dataset_out_po["stage"],
            env=self.dataset_out_po["env"],
            version=self.dataset_out_po["version"],
            version_control=self.dataset_out_po["version_control"],
            data=data,
        )
        return dataset


# ------------------------------------------------------------------------------------------------ #
#                                   TRAIN TEST SPLIT                                               #
# ------------------------------------------------------------------------------------------------ #
class TrainTestSplit(DatasetOperator):
    """Splits the dataset into to training and test sets by user

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        clustered (bool): Whether to cluster sampling.
        clustered_by (str): The column by which to cluster.
        train_proportion (float): The proportion of the dataset to allocate to training.
        random_state (int): PseudoRandom generator seed
        version_control (bool): If True, bump the version if the file exists.

    Returns: Dictionary of Dataset objects containing train and test Dataset objects.

    """

    def __init__(
        self,
        dataset_in_po: dict,
        dataset_out_po: dict,
        clustered_by: str = None,
        clustered: bool = False,
        train_proportion: float = 0.8,
        random_state: int = None,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        super().__init__(
            dataset_in_po=dataset_in_po,
            dataset_out_po=dataset_out_po,
            clustered=clustered,
            clustered_by=clustered_by,
            train_proportion=train_proportion,
            random_state=random_state,
            name=name,
            description=description,
            version_control=version_control,
        )

    @repository
    def execute(self, *args, **kwargs) -> Dict[str, Dataset]:

        data = self.input_data.data

        if self.clustered:

            clusters = data[self.clustered_by].unique()
            train_set_size = int(len(clusters) * self.train_proportion)

            train_clusters = default_rng.choice(
                a=clusters, size=train_set_size, replace=False, shuffle=True
            )
            test_clusters = np.setdiff1d(clusters, train_clusters)

            train_set = data.loc[data[self.clustered_by].isin(train_clusters)]
            test_set = data.loc[data[self.clustered_by].isin(test_clusters)]

        else:
            # Get all indices
            index = np.array(data.index.to_numpy())

            # Split the training set by the train proportion
            train_set = data.sample(frac=self.train_proportion, replace=False, axis=0)

            # Obtain training indices and perform setdiff to get test indices
            train_idx = train_set.index
            test_idx = np.setdiff1d(index, train_idx)

            # Extract test data
            test_set = data.loc[test_idx]

        # Create train and test Dataset objects.
        train = self._output_dataset_params["train"].to_dataset()
        train.data = train_set

        test = self._output_dataset_params["test"].to_dataset()
        test.data = test_set

        outputs = {"train": train, "test": test}

        return outputs


# ------------------------------------------------------------------------------------------------ #


class RatingsAdjuster(DatasetOperator):
    """Centers the ratings by subtracting the users average rating from each of the users ratings.

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        version_control (bool): If True, bump the version if the file exists.

    Returns Dataset
    """

    def __init__(
        self,
        input_dataset_params: DatasetParams,
        output_dataset_params: DatasetParams,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        super().__init__(
            name=name,
            description=description,
            input_dataset_params=input_dataset_params,
            output_dataset_params=output_dataset_params,
            version_control=version_control,
        )

    def execute(self, *args, **kwargs) -> Dataset:

        data = self.input_data.data

        data["adj_rating"] = data["rating"].sub(data.groupby("userId")["rating"].transform("mean"))

        dataset = self._output_dataset_params.to_dataset()
        dataset.data = data

        return dataset


class User(DatasetOperator):
    """Computes and stores average rating for each user.

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        version_control (bool): If True, bump the version if the file exists.

    Returns Dataset
    """

    def __init__(
        self,
        input_dataset_params: DatasetParams,
        output_dataset_params: DatasetParams,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        super().__init__(
            name=name,
            description=description,
            input_dataset_params=input_dataset_params,
            output_dataset_params=output_dataset_params,
            version_control=version_control,
        )

    def execute(self, *args, **kwargs) -> Dataset:

        data = self.input_data.data

        user_average_ratings = data.groupby("userId")["rating"].mean().reset_index()
        user_average_ratings.columns = ["userId", "mean_rating"]

        dataset = self._output_dataset_params.to_dataset()
        dataset.data = user_average_ratings

        return dataset


# ------------------------------------------------------------------------------------------------ #
class Phi(DatasetOperator):
    """Produces the Phi dataframe which contains every combination of users with rated films in common.

    This output will be on the order of N^2M and will be written to file. This class will create a DataFrame for each movie of the format:
    - movieId (int)
    - user (int): A user that rated movieId
    - neighbor (int): A user who also rated movieId

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        version_control (bool): If True, bump the version if the file exists.

    Returns Dataset
    """

    def __init__(
        self,
        input_dataset_params: DatasetParams,
        output_dataset_params: DatasetParams,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        super().__init__(
            name=name,
            description=description,
            input_dataset_params=input_dataset_params,
            output_dataset_params=output_dataset_params,
            version_control=version_control,
        )

    def execute(self, *args, **kwargs) -> Dataset:

        data = self.input_data.data

        phi = data.merge(data, how="inner", on="movieId")
        # Remove rows where userId_x and userId_y are equal
        phi = phi.loc[phi["userId_x"] != phi["userId_y"]]

        dataset = self._output_dataset_params.to_dataset()
        dataset.data = phi

        return dataset


# ------------------------------------------------------------------------------------------------ #
class UserWeights(DatasetOperator):
    """Computes user-user pearson correlation coefficients representing similarity between users.

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        version_control (bool): If True, bump the version if the file exists.

    Returns Dataset
    """

    def __init__(
        self,
        input_dataset_params: DatasetParams,
        output_dataset_params: DatasetParams,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        super().__init__(
            name=name,
            description=description,
            input_dataset_params=input_dataset_params,
            output_dataset_params=output_dataset_params,
            version_control=version_control,
        )

    def execute(self, *args, **kwargs) -> Dataset:
        """Executes the operation

        Args:
            data (pd.DataFrame): The user neighbor rating data
        """

        data = self.input_data.data

        weights = self._compute_weights(data=data)

        dataset = self._output_dataset_params.to_dataset()
        dataset.data = weights

    def _compute_weights(self, data: pd.DataFrame) -> pd.DataFrame:
        """Computes the pearson's correlation for each user and her neighbors

        Technically, the algorithm calls for pearson's correlation coefficient, which
        centers the data. Since the ratings have already been centered,
        the calculation below is equivalent to cosine similarity.

        Args:
            data (pd.DataFrame): The dataframe containing users and neighbors
        """

        weights = (
            data.groupby(["userId_x", "userId_y"])
            .progress_apply(
                lambda x: (
                    np.dot(x["adj_rating_x"], x["adj_rating_y"])
                    / (
                        np.sqrt(
                            np.sum(np.square(x["adj_rating_x"]))
                            * np.sum(np.square(x["adj_rating_y"]))
                        )
                    )
                )
            )
            .reset_index()
        )

        weights.columns = ["userId", "neighbor", "weight"]

        return weights


# ------------------------------------------------------------------------------------------------ #


class DataIntegrator(DatasetOperator):
    """Integrates user, rating, and weight data

    Args:
        name (str): Name given to this instance of the operator.
        description (str): Description assigned to this instance of the operator
        input_dataset_params (str): A dataset parameter object or list of objects, defining the input.
        output_dataset_params (dict): Dictionary of parameter objects for the train and test datasets.
        version_control (bool): If True, bump the version if the file exists.

    Returns Dataset
    """

    def __init__(
        self,
        input_dataset_params: DatasetParams,
        output_dataset_params: DatasetParams,
        name: str = None,
        description: str = None,
        version_control: bool = True,
    ) -> None:
        name = self.__class__.__name__.lower() if name is None else name
        super().__init__(
            name=name,
            description=description,
            input_dataset_params=input_dataset_params,
            output_dataset_params=output_dataset_params,
            version_control=version_control,
        )
        self._users = None
        self._ratings = None
        self._weights = None

    def execute(self, **kwargs) -> None:
        """Executes the operation

        Args:
            data (pd.DataFrame): Not used.
        """
        self._load_data()

        # Add Users and Weights
        data = self._users.merge(self._weights, how="left", on="userId")
        # Merge in ratings for the neighbors into the dataframe
        data = data.merge(self._ratings, how="left", left_on="neighbor", right_on="userId")

        dataset = self._output_dataset_params.to_dataset()
        dataset.data = data

        return dataset

    def _load_data(self) -> None:
        """Loads user, ratings, and weights data"""

        self._users = self.input_data["users"]
        self._ratings = self.input_data["ratings"]
        self._weights = self.input_data["weights"]


# ------------------------------------------------------------------------------------------------ #