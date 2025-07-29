import logging
import os
from typing import Optional

import numpy
import psutil
from easytrajh5.fs import load_yaml_dict, dump_yaml
from path import Path
from rich.pretty import pprint
from server import readers
from server.readers import get_traj_reader

logger = logging.getLogger(__name__)
traj_reader: Optional[readers.RshowReaderMixin] = None


def select_new_key(foam_id, key):
    if "opt_keys" in traj_reader.config:
        config = traj_reader.config
        config.key = key
        config.matrix = config.matrix_by_key[config.key]


def init(config):
    global traj_reader
    traj_reader = get_traj_reader(config)


def reset_foam_id(foam_id):
    return {"success": True}


def get_tags(foam_id):
    return traj_reader.get_tags()


def get_config(foam_id, k):
    return traj_reader.get_config(k)


def kill():
    if not traj_reader.get_config("is_dev"):
        psutil.Process(os.getpid()).kill()


def get_pdb_lines(foam_id, i_frame_traj):
    return traj_reader.get_pdb_lines(i_frame_traj)


def get_pdb_lines_with_as_communities(foam_id, i_frame_traj):
    return traj_reader.get_pdb_lines_with_as_communities(i_frame_traj)


def get_pdb_lines_with_as_pockets(foam_id, i_frame_traj):
    return traj_reader.get_pdb_lines_with_as_pockets(i_frame_traj)


def get_views(foam_id):
    return traj_reader.get_views()


def update_view(foam_id, view):
    return traj_reader.update_view(view)


def delete_view(foam_id, view):
    return traj_reader.delete_view(view)


def get_json_datasets(foam_id):
    return []


def get_json(foam_id, key):
    return {}


def get_parmed_blob(foam_id, i_frame=None):
    pass


def get_min_frame(foam_id):
    if not hasattr(traj_reader, "config"):
        return None
    config = traj_reader.config
    if not config.metad_dir:
        return None

    min_yaml = Path(config.metad_dir) / "min.yaml"
    if min_yaml.exists():
        min_frame = load_yaml_dict(min_yaml).get("iframe")
        if min_frame is not None:
            logger.info(f"read min_frame from {min_yaml}: {min_frame}")
            return min_frame

    def get_i_frame_min(matrix):
        entries = []
        n_row = len(matrix)
        n_col = len(matrix[0])
        cutoff = 0.05
        for i_row, row in enumerate(matrix):
            for i_col, cell in enumerate(row):
                fr_col = i_col / n_col
                if fr_col < cutoff or fr_col > (1 - cutoff):
                    continue
                fr_row = i_row / n_row
                if fr_row < cutoff or fr_row > (1 - cutoff):
                    continue
                if "iFrameTraj" in cell and "p" in cell:
                    entries.append(
                        {
                            "i_frame": cell["iFrameTraj"][0],
                            "p": float(cell["p"]),
                        }
                    )
        entries.sort(key=lambda e: e["p"])
        return entries[0]["i_frame"] if len(entries) else None

    try:
        min_frame = get_i_frame_min(config.matrix)
        logger.info(f"min_frame {min_frame}")
        dump_yaml({"iframe": min_frame}, min_yaml)
    except Exception:
        logger.warning("couldn't find min_frame")
        min_frame = None

    return min_frame


def get_distances(foam_id, dpairs):
    traj_file = traj_reader.traj_manager.get_traj_file(0)

    atom_indices = traj_file.atom_indices
    if atom_indices is None:
        atom_indices = list(range(traj_file.topology.n_atoms))

    i_raw_atom_by_i_atom = {}
    for dpair in dpairs:
        for i_atom in dpair["i_atom1"], dpair["i_atom2"]:
            i_raw_atom_by_i_atom[i_atom] = atom_indices[i_atom]
    lookup_atom_indices = list(i_raw_atom_by_i_atom.values())
    lookup_atom_indices.sort()

    topology = traj_file.fetch_topology(atom_indices)
    for dpair in dpairs:
        atom1 = topology.atom(dpair["i_atom1"])
        atom2 = topology.atom(dpair["i_atom2"])
        dpair["label"] = f"{atom1}::{atom2}"

    n_frame = traj_file.get_n_frame()
    data = traj_file.read_atom_dataset_progressively(
        "coordinates", slice(0, n_frame), lookup_atom_indices
    )
    pprint(data.shape)

    def get_i(i_atom):
        i_raw_atom = i_raw_atom_by_i_atom[i_atom]
        return lookup_atom_indices.index(i_raw_atom)

    for dpair in dpairs:
        pprint(dpair)
        i_atom1 = get_i(dpair["i_atom1"])
        i_atom2 = get_i(dpair["i_atom2"])
        values = []
        for i_frame in range(n_frame):
            p1 = data[i_frame][i_atom1]
            p2 = data[i_frame][i_atom2]
            values.append(numpy.linalg.norm(p1 - p2) * 10)
        dpair["values"] = values

    return dpairs
