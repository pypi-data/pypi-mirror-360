import os
from typing_extensions import Literal
from . import export_slcf_raw, export_obst_raw, export_smoke_raw
from .. import Simulation


def export_sim(sim: Simulation, output_dir: str, ordering: Literal['C', 'F'] = 'C'):
    """Exports the 3d arrays to raw binary files with corresponding .yaml meta files.
        Warning: This method does not work for large simulations as some internal multiprocess buffers overflow after
        a few GB of data. Please export the simulation manually using the functions used in this method in separate
        python instances.

    :param sim: The :class:`Simulation` to export.
    :param output_dir: The directory in which to save all files.
    :param ordering: Whether to write the data in C or Fortran ordering.
    """
    meta = {"Obstructions": list(), "Slices": list(), "Volumes": list(), "Hash": sim._hash}

    for obst in sim.obstructions:
        obst_path = export_obst_raw(obst, os.path.join(output_dir, "obst"), ordering)
        if obst_path:
            meta["Obstructions"].append(os.path.relpath(obst_path, output_dir).replace("\\", "/"))

    for slc in sim.slices:
        slice_path = export_slcf_raw(slc, os.path.join(output_dir, "slices", slc.quantity.name.replace(' ', '_').lower()), ordering)
        if slice_path:
            meta["Slices"].append(os.path.relpath(slice_path, output_dir).replace("\\", "/"))

    for smoke in sim.smoke_3d:
        volume_path = export_smoke_raw(smoke, os.path.join(output_dir, "smoke", smoke.quantity.name.replace(' ', '_').lower()), ordering)
        if volume_path:
            meta["Volumes"].append(os.path.relpath(volume_path, output_dir).replace("\\", "/"))

    meta["NumObstructions"] = len(meta["Obstructions"])
    meta["NumSlices"] = len(meta["Slices"])
    meta["NumVolumes"] = len(meta["Volumes"])

    import yaml
    meta_file_path = os.path.join(output_dir, sim.chid + "-smv.yaml")
    with open(meta_file_path, 'w') as metafile:
        yaml.dump(meta, metafile)

    return meta_file_path
