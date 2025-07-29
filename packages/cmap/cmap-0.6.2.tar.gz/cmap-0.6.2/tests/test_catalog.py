from itertools import chain

import numpy as np
import pytest

from cmap import Colormap
from cmap._catalog import Catalog

catalog = Catalog()


@pytest.mark.filterwarnings("ignore:The name:")
def test_catalog_data() -> None:
    """Test that all catalog data is one of a couple normalized types."""
    for name, item in catalog.items():
        if isinstance(item.data, list):
            item_lengths = [len(x) for x in item.data]
            assert len(set(item_lengths)) == 1
            if item_lengths[0] == 2:
                assert all(len(x[1]) == 3 for x in item.data) or all(
                    len(x[1]) == 4 for x in item.data
                )
            else:
                assert item_lengths[0] in (3, 4)
        elif callable(item.data):
            x = np.linspace(0, 1, 256)
            assert item.data(x).shape in ((256, 3), (256, 4))
        else:
            raise AssertionError(f"Unexpected data type: {type(item.data)}")
        Colormap(name)  # smoke test

    assert len(catalog) > 100


def test_lower_map() -> None:
    # make sure the lower map is the same length as the original
    # ... i.e. that we have no name collisions
    assert len(catalog._data) == len(catalog._data)


def test_data_loading() -> None:
    for name in catalog._original_names:
        Colormap(name)


def test_catalog_names() -> None:
    assert "bids:viridis" in catalog.namespaced_keys()
    assert "viridis" in catalog.short_keys()
    assert [
        catalog.resolve(x)
        for x in chain(catalog.short_keys(), catalog.namespaced_keys())
    ]
    with pytest.raises(KeyError):
        catalog.resolve("not-a-cmap")

    unique = catalog.unique_keys(prefer_short_names=True, normalized_names=False)
    assert "ice" not in unique
    assert "viridis" in unique
    assert "cmocean:ice" in unique
    assert "YlGn" in unique
    unique = catalog.unique_keys(prefer_short_names=False, normalized_names=True)
    assert "colorbrewer:ylgn" in unique
    assert "colorbrewer:YlGn" not in unique
    assert "viridis" not in unique
    assert "bids:viridis" in unique
    assert "matplotlib:viridis" not in unique

    assert "viridis" not in catalog.unique_keys(categories=("cyclic",))
    assert "viridis" in catalog.unique_keys(categories=("sequential",))
    assert "viridis" not in catalog.unique_keys(interpolation="nearest")
    assert "viridis" in catalog.unique_keys(interpolation="linear")
