import csv
import logging
from path import Path
from abc import ABC, abstractmethod
from typing import Any
import os
import sys

import mdtraj
import numpy as np
from addict import Dict
from easytrajh5.fs import (
    dump_yaml,
    get_checked_path,
    load_yaml,
)
from easytrajh5.manager import TrajectoryManager
from easytrajh5.pdb import filter_for_atom_lines, get_pdb_lines_of_traj_frame
from easytrajh5.select import select_mask, slice_parmed
from easytrajh5.struct import (
    get_parmed_from_mdtraj,
    get_mdtraj_from_parmed,
    get_parmed_from_parmed_or_pdb,
)
from pydash import py_
from rdkit import Chem
from rdkit.Chem.rdmolfiles import MolToPDBBlock
from rich.pretty import pretty_repr

from server.alphaspace import AlphaSpace

logger = logging.getLogger(__name__)


def check_files(*args):
    for a in args:
        if not Path(a).exists():
            print(f"File not found: {a}")
            sys.exit(1)


class RshowReaderMixin(ABC):
    """
    Interface to the handlers
    """

    def __init__(self, config={}):
        self.config = Dict(
            mode="strip",  # "strip", "matrix", "sparse-matrix", "matrix-strip", "table"
            strip=[],  # Dictionary of frame, traj, colours for use in trajolecule
            title="",  # Title for trajolecule
            is_solvent=True,
        )
        self.config.update(config)
        for l in repr_lines(self.config, f"{self.__class__.__name__}.config = "):
            logger.info(l)

        self.traj_manager = None
        self.i_frame_traj = None
        self.atom_indices_by_i_traj = {}
        self.frame = None

        if "work_dir" in config:
            os.chdir(config["work_dir"])
        self.process_config()

    @abstractmethod
    def process_config(self):
        pass

    @abstractmethod
    def get_config(self, k) -> Any:
        pass

    @abstractmethod
    def get_tags(self) -> dict:
        pass

    @abstractmethod
    def read_frame_traj(self, i_frame_traj: [int, int] = None) -> mdtraj.Trajectory:
        pass

    def get_pdb_lines(self, i_frame_traj):
        logger.info(f"pdb {i_frame_traj}")
        return filter_for_atom_lines(
            get_pdb_lines_of_traj_frame(self.read_frame_traj(i_frame_traj))
        )

    def get_pdb_lines_with_as_communities(self, i_frame_traj: [int, int]):
        frame = self.read_frame_traj(i_frame_traj)
        pdb_lines = filter_for_atom_lines(get_pdb_lines_of_traj_frame(frame))

        pmd = get_parmed_from_mdtraj(frame)
        i_protein_atoms = select_mask(pmd, "diff {protein} {mdtraj type H}")

        alpha_space = AlphaSpace(frame.atom_slice(i_protein_atoms))
        alpha_space_pdb_lines = alpha_space.get_community_pdb_lines()

        alpha_pdb = "alphaspace.pdb"
        with open(alpha_pdb, "w") as f:
            f.write("\n".join(alpha_space_pdb_lines))

        pdb_lines.extend(alpha_space_pdb_lines)
        return pdb_lines

    def get_pdb_lines_with_as_pockets(self, i_frame_traj: [int, int]):
        frame = self.read_frame_traj(i_frame_traj)
        pdb_lines = filter_for_atom_lines(get_pdb_lines_of_traj_frame(frame))

        pmd = get_parmed_from_mdtraj(frame)
        i_protein_atoms = select_mask(pmd, "diff {protein} {mdtraj type H}")

        alpha_space = AlphaSpace(frame.atom_slice(i_protein_atoms))
        alpha_space_pdb_lines = alpha_space.get_pocket_pdb_lines()

        alpha_pdb = "alphaspace.pdb"
        with open(alpha_pdb, "w") as f:
            f.write("\n".join(alpha_space_pdb_lines))

        pdb_lines.extend(alpha_space_pdb_lines)
        return pdb_lines

    def get_views(self):
        return []

    def update_view(self, view):
        return {}

    def delete_view(self, view):
        return {}

    def close(self):
        pass


def get_traj_reader(config) -> RshowReaderMixin:
    """
    :param config: dict
        reader_class: str - name of RshowReaderMixin
    :return: RshowReaderMixin
    """
    if config.reader_class not in globals():
        raise ValueError(f"Couldn't find reader_class {config.reader_class}")
    TrajReaderClass = globals()[config.reader_class]
    return TrajReaderClass(config)


def get_i_view(views, test_view):
    for i, view in enumerate(views):
        if view["id"] == test_view["id"]:
            return i
    return None


def update_view(views, update_view):
    i = get_i_view(views, update_view)
    if i is not None:
        views[i] = update_view
    else:
        views.insert(0, update_view)
    return views


def delete_view(views, to_delete_view):
    i = get_i_view(views, to_delete_view)
    if i is not None:
        del views[i]
    return views


def repr_lines(o, prefix=""):
    lines = pretty_repr(o).split("\n")
    lines[0] = prefix + lines[0]
    return lines


class TrajReader(RshowReaderMixin):
    """
    FrameReader(config)

    :param config: dict:
         trajectories: [str]
         strip: Optional[dict]
             -   iFrameTraj: [int, int]
                 p: float - [0,1]
         is_solvent: bool

    saves views to <trajectories[0]:stem>.views.yaml
    """

    def get_traj_manager(self) -> TrajectoryManager:
        paths = self.config.trajectories
        is_not_writeable = any((not Path(p).access(os.R_OK | os.W_OK)) for p in paths)
        mode = "r" if is_not_writeable else "a"
        if mode == "r":
            logger.info("Files are not writeable: read-only mode")
        is_dry_cache = not self.config.is_solvent
        return TrajectoryManager(paths, mode=mode, is_dry_cache=is_dry_cache)

    def get_tags(self):
        names = [Path(t).name for t in self.config.trajectories]
        if len(names) == 1:
            return {"h5": names[0]}
        elif len(names) >= 1:
            name = ";".join(names)
            if len(name) > 20:
                name = name[:40] + "..."
            return {"h5": name}
        else:
            raise ValueError("No trajectories found.")

    def process_config(self):
        self.config.title = self.get_tags()
        self.traj_manager = self.get_traj_manager()
        f = Path(self.config.trajectories[0])
        self.views_yaml = f.with_suffix(".views.yaml")
        self.config.mode = "strip"
        self.config.strip = []
        for i_traj in range(self.traj_manager.get_n_trajectories()):
            n_frame = self.traj_manager.get_n_frame(i_traj)
            self.config.strip.append(
                [dict(iFrameTraj=[i, i_traj], p=i / n_frame) for i in range(n_frame)]
            )

    def close(self):
        if hasattr(self, "traj_manager"):
            self.traj_manager.close()

    def get_config(self, k):
        return self.config[k]

    def read_frame_traj(
        self, i_frame_traj=None, atom_mask="intersect {protein} {amber @CA}"
    ):
        if i_frame_traj and i_frame_traj != self.i_frame_traj:
            new_frame = self.traj_manager.read_as_frame_traj(i_frame_traj)
            atom_indices = None
            if atom_mask:
                i_traj = i_frame_traj[1]
                if (i_traj, atom_mask) not in self.atom_indices_by_i_traj:
                    atom_indices = select_mask(
                        get_parmed_from_mdtraj(new_frame), atom_mask
                    )
                    self.atom_indices_by_i_traj[(i_traj, atom_mask)] = atom_indices
                else:
                    atom_indices = self.atom_indices_by_i_traj[(i_traj, atom_mask)]
            if self.frame is not None:
                new_frame.xyz = np.copy(new_frame.xyz)
                if atom_mask:
                    new_frame.superpose(
                        self.frame,
                        atom_indices=atom_indices,
                        ref_atom_indices=self.atom_indices,
                    )
                else:
                    new_frame.superpose(self.frame)
            self.frame = new_frame
            self.atom_indices = atom_indices
            self.i_frame_traj = i_frame_traj
        return self.frame

    def get_views(self):
        if self.views_yaml.exists():
            result = load_yaml(self.views_yaml)
            if isinstance(result, list):
                return result
        return []

    def update_view(self, view):
        views = self.get_views()
        update_view(views, view)
        dump_yaml(views, self.views_yaml)
        return {}

    def delete_view(self, to_delete_view):
        views = self.get_views()
        delete_view(views, to_delete_view)
        logger.info(f"delete_view view:{to_delete_view['id']}")
        dump_yaml(views, self.views_yaml)


class FrameReader(TrajReader):
    """
    FrameReader(config)

    :param config: dict:
        pdb_or_parmed: str
        is_solvent: bool

    saves views to <config.pdb_or_parmed:stem>.views.yaml
    """

    def process_config(self):
        self.config.title = self.config.pdb_or_parmed
        self.config.mode = "frame"
        fname = Path(self.config.pdb_or_parmed)
        check_files(fname)
        pmd = get_parmed_from_parmed_or_pdb(fname)
        if not self.config.is_solvent:
            i_atoms = select_mask(pmd, "not {solvent}")
            pmd = slice_parmed(pmd, i_atoms)
        self.frame = get_mdtraj_from_parmed(pmd)
        self.views_yaml = fname.absolute().with_suffix(".views.yaml")
        return True

    def read_frame_traj(self, i_frame_traj=None, atom_mask=None):
        return self.frame

    def get_tags(self):
        fname = self.config.title.lower()
        if fname.endswith("parmed"):
            key = "parmed"
        elif fname.endswith("pdb"):
            key = "pdb"
        else:
            key = "file"
        return {key: self.config.title}


def get_first_value(matrix):
    value = py_.head(
        py_.filter(py_.flatten_deep(matrix), lambda v: py_.has(v, "iFrameTraj"))
    )
    if value is not None:
        return value
    value = py_.head(
        py_.filter(py_.flatten_deep(matrix), lambda v: py_.has(v, "iFrameTrajs"))
    )
    if value is not None:
        return value
    return None


class MatrixTrajReader(TrajReader):
    """
    FrameReader(config)

    :param config:
        matrix_yaml: str
        is_solvent: bool # handled by

    matrix_yaml has structure: dict:
        trajectories: [str]
        key: optional[str]
        matrix:
        -
            - Optional[dict]
                p: float # 0 to 1
                iFrameTraj: [int, int]
        other:
             -   key: str
                 matrix:
                     -
                         - Optional[dict]
                             p: float # 0 to 1
                             iFrameTraj: [int, int]

    saves views to <config.matrix_yaml:stem>.views.yaml
    """

    def process_config(self):
        matrix_yaml = Path(self.config.matrix_yaml)
        if matrix_yaml.is_dir():
            matrix_yaml = matrix_yaml / "matrix.yaml"
        check_files(matrix_yaml)

        logger.info(f"reading {matrix_yaml}...")
        payload = load_yaml(matrix_yaml, is_addict=True)
        if py_.has(payload, "matrix"):
            self.config.matrix = payload["matrix"]
        else:
            self.config.matrix = payload

        self.config.matrix_by_key = {}
        if "other" in payload:
            logger.info("Loading alternate matrices")
            self.config.matrix_by_key[payload.get("key")] = self.config.matrix
            for entry in payload["other"]:
                self.config.matrix_by_key[entry["key"]] = entry["matrix"]
            self.config["opt_keys"] = list(self.config.matrix_by_key.keys())
            if py_.has(payload, "key") and not self.config.key:
                self.config.key = payload["key"]
            if py_.get(self.config, "key"):
                logger.info(f"Set opt_keys {self.config.opt_keys} - {self.config.key}")
                self.config.matrix = self.config.matrix_by_key[self.config.key]

        logger.info("matrix loaded")

        # figure out if matrix has dense iFrameTraj
        self.config.mode = "matrix"
        for cell in py_.flatten_deep(self.config.matrix):
            if not cell:
                continue
            if py_.has(cell, "p") and not py_.has(cell, "iFrameTraj"):
                self.config.mode = "sparse-matrix"
                break

        # set i_frame_first
        value = get_first_value(self.config.matrix)
        self.config.i_frame_first = value["iFrameTraj"][0]

        self.views_yaml = matrix_yaml.absolute().with_suffix(".views.yaml")
        logger.info(f"views_yaml: {self.views_yaml}")

        matrix_yaml.absolute().parent.chdir()
        self.config.trajectories = payload.trajectories
        self.traj_manager = self.get_traj_manager()

        self.config.title = "Matrix"


class LigandsReceptorReader(TrajReader):
    """
    FrameReader(config)

    :param config:
        pdb: str
        ligands: str
        csv: str
        is_solvent: bool

    saves views to <trajectories[0]:stem>.views.yaml
    """

    def process_config(self):
        self.config.title = f"{Path(self.config.pdb).name}"
        self.config.mode = "table"

        pdb = get_checked_path(self.config.pdb)
        check_files(pdb)
        self.frame = mdtraj.load_pdb(str(pdb))
        self.receptor_lines = get_pdb_lines_of_traj_frame(self.frame)

        sdf = get_checked_path(self.config.ligands)
        self.mols = list(Chem.SDMolSupplier(sdf))
        n = len(self.mols)

        labels = []
        for i_mol, mol in enumerate(self.mols):
            label = mol.GetProp("_Name")
            if not label:
                label = f"Molecule {i_mol}"
            labels.append(label)

        self.config.table_headers = ["title", "i"]
        self.config.table = [
            dict(iFrameTraj=[i, 0], p=i / n, vals=[labels[i], i]) for i in range(n)
        ]

        # additional columns
        if self.config.csv:
            with open(get_checked_path(self.config.csv)) as f:
                for i, row in enumerate(csv.reader(f)):
                    if i == 0:
                        self.config.table_headers.extend(row)
                    elif i > n:
                        break
                    else:
                        row = [round(float(x), 3) for x in row]
                        self.config.table[i - 1]["vals"].extend(row)

        self.views_yaml = Path(pdb).absolute().with_suffix(".views.yaml")
        self.views_yaml.touch()

    def get_ligand_pdb_lines(self, i_ligand):
        return MolToPDBBlock(self.mols[i_ligand]).splitlines()

    def get_pdb_lines(self, i_frame_traj):
        i_frame = i_frame_traj[0]
        return self.receptor_lines + self.get_ligand_pdb_lines(i_frame)

    def get_tags(self):
        return {"fname": self.config.title}
