import pytest

from datalad_core.constraints import ConstraintError
from datalad_core.dsops.create import create_dataset


def test_create_dataset_invalid_arg(tmp_path):
    with pytest.raises(
        ConstraintError,
        match='cannot assign an annex description with no annex',
    ):
        create_dataset(
            path=tmp_path,
            annex=False,
            annex_description='some',
        )


def test_create_dataset(tmp_path):
    ds = list(create_dataset(path=tmp_path))
    ds = list(create_dataset(dataset=tmp_path))
