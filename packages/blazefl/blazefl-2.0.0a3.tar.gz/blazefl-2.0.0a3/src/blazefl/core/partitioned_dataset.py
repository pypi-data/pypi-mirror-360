from enum import StrEnum
from typing import Protocol, TypeVar

from torch import Generator
from torch.utils.data import DataLoader, Dataset

PartitionType = TypeVar("PartitionType", bound=StrEnum, contravariant=True)


class PartitionedDataset(Protocol[PartitionType]):
    """
    Abstract base class for partitioned datasets in federated learning.

    This class defines the interface for managing datasets that are partitioned
    across multiple clients.

    Raises:
        NotImplementedError: If the methods are not implemented in a subclass.
    """

    def get_dataset(self, type_: PartitionType, cid: int | None) -> Dataset:
        """
        Retrieve a dataset for a specific type and client ID.

        Args:
            type_ (str): The type of the dataset.
            cid (int | None): The client ID.

        Returns:
            Dataset: The dataset.
        """
        ...

    def set_dataset(
        self, type_: PartitionType, cid: int | None, dataset: Dataset
    ) -> None:
        """
        Set a dataset for a specific type and client ID.

        Args:
            type_ (str): The type of the dataset.
            cid (int | None): The client ID.
            dataset (Dataset): The dataset to set.
        """
        ...

    def get_dataloader(
        self,
        type_: PartitionType,
        cid: int | None,
        batch_size: int | None,
        generator: Generator | None,
    ) -> DataLoader:
        """
        Retrieve a DataLoader for a specific type, client ID, and batch size.

        Args:
            type_ (str): The type of the dataset.
            cid (int | None): The client ID.
            batch_size (int | None): The batch size.
            generator (Generator | None):
                Optional random number generator for shuffling.

        Returns:
            DataLoader: The DataLoader.
        """
        ...
