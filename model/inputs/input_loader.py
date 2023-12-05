"""File contains code associated with loading the input data."""
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from model.inputs.pre_processing import PreProcessorBase

logger = logging.getLogger(__name__)


class InputLoader:
    """
    Class responsible for containing all code associated with reading input data
    """

    def __init__(self, pre_processor: Optional[PreProcessorBase] = None) -> None:
        """
        Initialises the InputLoader class.
        :param pre_processor: Pre-processor to use on the input data
        """
        self.pre_processor = pre_processor

    def read(self, file_path: Path) -> pd.DataFrame:
        """
        Reads a csv file into a pandas dataframe. If a pre-processor is specified, the data is pre-processed.
        :param file_path: Path to the file to read
        :return: Pandas dataframe containing the data
        """
        logger.info(f"Reading file at {file_path} 📖")
        try:
            if self.pre_processor is not None:
                return self.pre_processor.pre_process(pd.read_csv(file_path))
            else:
                pd.read_csv(file_path)
        except IOError:
            logger.error(f"Could not read file at {file_path}")
