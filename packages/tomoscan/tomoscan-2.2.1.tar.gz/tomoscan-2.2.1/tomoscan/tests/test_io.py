import os
import h5py
import numpy

from tomoscan.io import check_virtual_sources_exist


def test_vds(tmp_path):
    h5_file_without_vds = os.path.join(tmp_path, "h5_file_without_vds.hdf5")

    with h5py.File(h5_file_without_vds, mode="w") as h5f:
        h5f["data"] = numpy.random.random((120, 120))
    assert check_virtual_sources_exist(h5_file_without_vds, "data")

    h5_file_with_vds = os.path.join(tmp_path, "h5_file_with_vds.hdf5")

    # create some dataset
    for i in range(4):
        filename = os.path.join(tmp_path, f"{i}.h5")
        with h5py.File(filename, mode="w") as h5f:
            h5f.create_dataset("data", (100,), "i4", numpy.arange(100))

    layout = h5py.VirtualLayout(shape=(4, 100), dtype="i4")
    for i in range(4):
        filename = os.path.join(tmp_path, f"{i}.h5")
        layout[i] = h5py.VirtualSource(filename, "data", shape=(100,))

    with h5py.File(h5_file_with_vds, mode="w") as h5f:
        # create the virtual dataset
        h5f.create_virtual_dataset("data", layout, fillvalue=-5)
    assert check_virtual_sources_exist(h5_file_with_vds, "data")
