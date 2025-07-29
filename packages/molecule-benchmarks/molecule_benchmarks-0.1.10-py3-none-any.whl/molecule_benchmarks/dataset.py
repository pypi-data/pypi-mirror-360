import csv
import itertools
import multiprocessing as mp
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Optional, TypeVar

import requests
from rdkit import Chem
from tqdm import tqdm

from molecule_benchmarks.moses_metrics import mapper  # type: ignore
from molecule_benchmarks.utils import download_with_cache


class SmilesDataset:
    @classmethod
    def load_qm9_dataset(
        cls, max_train_samples: Optional[int] = None, cache_dir: str | Path = "data"
    ):
        """Load the QM9 dataset."""
        ds_url = (
            "https://huggingface.co/datasets/n0w0f/qm9-csv/resolve/main/qm9_dataset.csv"
        )
        content = download_with_cache(ds_url, cache_dir=cache_dir)
        smiles = []

        reader = csv.DictReader(content.splitlines())

        for row in reader:
            smiles.append(row["smiles"])  # Assuming the column name is "smiles"
        # smiles = canonicalize_smiles_list(smiles)
        random.seed(42)  # For reproducibility
        random.shuffle(smiles)
        fraction = 1.0
        num_train_samples = int(len(smiles) * 0.8)
        num_val_samples = len(smiles) - num_train_samples
        if max_train_samples is not None:
            max_train_samples = min(max_train_samples, int(len(smiles) * 0.8))
            fraction = max_train_samples / num_train_samples
            num_train_samples = int(max_train_samples)
            num_val_samples = int(num_val_samples * fraction)

        train_smiles = smiles[:num_train_samples]
        validation_smiles = smiles[
            num_train_samples : num_train_samples + num_val_samples
        ]
        return cls(train_smiles=train_smiles, validation_smiles=validation_smiles)

    @classmethod
    def load_guacamol_dataset(
        cls, max_train_samples: Optional[int] = None, cache_dir: str | Path = "data"
    ):
        """Load the Guacamole dataset."""
        train_ds_url = "https://ndownloader.figshare.com/files/13612760"
        validation_ds_url = "https://ndownloader.figshare.com/files/13612766"
        # download the dataset into memory
        train_content = download_with_cache(train_ds_url, cache_dir=cache_dir)
        train_smiles = train_content.splitlines()
        random.seed(42)  # For reproducibility
        validation_content = download_with_cache(validation_ds_url, cache_dir=cache_dir)
        validation_smiles = validation_content.splitlines()
        if max_train_samples is not None:
            max_train_samples = min(max_train_samples, len(train_smiles))
            fraction = max_train_samples / len(train_smiles)
            train_smiles = random.sample(train_smiles, max_train_samples)
            validation_smiles = random.sample(
                validation_smiles, int(len(validation_smiles) * fraction)
            )
        return cls(train_smiles=train_smiles, validation_smiles=validation_smiles)

    @classmethod
    def load_moses_dataset(
        cls, max_train_samples: Optional[int] = None, cache_dir: str | Path = "data"
    ):
        """Load the Moses dataset."""

        def download_smiles(split: str) -> list[str]:
            """Download SMILES from a given URL split."""
            url = f"https://media.githubusercontent.com/media/molecularsets/moses/master/data/{split}.csv"
            content = download_with_cache(url, cache_dir=cache_dir)
            csv_file = content.splitlines()
            reader = csv.DictReader(csv_file)
            smiles = [row["SMILES"] for row in reader]
            return smiles

        train_smiles = download_smiles("train")
        validation_smiles = download_smiles("test")
        random.seed(42)  # For reproducibility
        if max_train_samples is not None:
            max_train_samples = min(max_train_samples, len(train_smiles))
            fraction = max_train_samples / len(train_smiles)
            train_smiles = random.sample(train_smiles, max_train_samples)
            validation_smiles = random.sample(
                validation_smiles, int(len(validation_smiles) * fraction)
            )
        return cls(train_smiles=train_smiles, validation_smiles=validation_smiles)

    @classmethod
    def load_dummy_dataset(cls):
        """Load a dummy dataset for testing purposes."""
        train_smiles = ["C1=CC=CC=C1", "C1=CC=CN=C1", "C1=CC=CO=C1"]
        validation_smiles = ["C1=CC=CC=C1", "C1=CC=CN=C1"]
        return cls(train_smiles=train_smiles, validation_smiles=validation_smiles)

    def __init__(
        self,
        train_smiles: list[str] | Path | str,
        validation_smiles: list[str] | Path | str,
    ) -> None:
        self.train_smiles = load_smiles(train_smiles)
        self.validation_smiles = load_smiles(validation_smiles)

    def get_train_smiles(self) -> list[str]:
        """Get the training SMILES."""
        return self.train_smiles

    def get_validation_smiles(self) -> list[str]:
        """Get the validation SMILES."""
        return self.validation_smiles

    def get_train_molecules(self) -> list[Chem.Mol | None]:
        """Get the training molecules."""
        return [Chem.MolFromSmiles(s) for s in self.train_smiles]

    def get_validation_molecules(self) -> list[Chem.Mol | None]:
        """Get the validation molecules."""
        return [Chem.MolFromSmiles(s) for s in self.validation_smiles]

    def __repr__(self) -> str:
        """String representation of the dataset."""
        return (
            f"SmilesDataset(train_size={len(self.train_smiles)}, "
            f"validation_size={len(self.validation_smiles)})"
        )


def load_smiles(smiles: list[str] | str | Path) -> list[str]:
    """Load SMILES from a file or a list. Canonicalizes the SMILES strings."""
    if isinstance(smiles, str):
        smiles = Path(smiles)
    if isinstance(smiles, Path):
        with smiles.open("r") as f:
            smiles = f.readlines()
    smiles = [s.strip() for s in smiles if s.strip()]
    canonicalized_smiles = canonicalize_smiles_list(
        smiles, stochastical_test_count=10000
    )
    # Filter out None values that couldn't be canonicalized
    return [s for s in canonicalized_smiles if s is not None]


T = TypeVar("T", str, Optional[str])


def _canonicalize_single_smiles(smiles: Optional[str]) -> Optional[str]:
    """Helper function to canonicalize a single SMILES string for multiprocessing."""
    if smiles is not None:
        try:
            return Chem.CanonSmiles(smiles)
        except Exception:
            return smiles
    return None


def canonicalize_smiles_list(
    smiles: list[str | None] | list[str],
    n_jobs: Optional[int] = None,
    stochastical_test_count: int | None = None,
):
    """Canonicalize a list of SMILES strings using multiprocessing with progress tracking.
    Args:
        smiles (list[str | None] | list[str]): List of SMILES strings to canonicalize.
        n_jobs (Optional[int]): Number of parallel jobs to run. If None, uses all available cores.
        stochastical_test_count (int | None): If provided, will sample this many elements from the list and test if they are cannonicalized already. If they are, the original smiles will be returned, assuming they are already canonicalized.
    Returns:
        list[str | None]: List of canonicalized SMILES strings, with None for invalid SMILES.
    """
    if stochastical_test_count is not None and len(smiles) > stochastical_test_count:
        # Sample a subset of the list to test if they are already canonicalized
        sample = random.sample(smiles, stochastical_test_count)
        canonicalized_samples = mapper(
            n_jobs=1, job_name="Testing if SMILES are already canonicalized"
        )(_canonicalize_single_smiles, sample)
        already_canonicalized = all(
            canonicalized_sample == sample[i]
            for i, canonicalized_sample in enumerate(canonicalized_samples)
        )
        if already_canonicalized:
            return smiles
    return mapper(n_jobs=n_jobs, job_name="Canonicalizing SMILES")(
        _canonicalize_single_smiles, smiles
    )
