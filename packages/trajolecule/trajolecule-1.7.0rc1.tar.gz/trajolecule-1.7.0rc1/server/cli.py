#!/usr/bin/env python
import logging
import click
from addict import Dict
from path import Path

from .app import open_url_in_background, run_server, init_logging

logger = logging.getLogger(__name__)
config = Dict(mode="", work_dir=str(Path.cwd()))
init_logging()


@click.group()
@click.option("--dev", is_flag=True, help="Run continuous server")
@click.option("--solvent", is_flag=True, help="Keep solvent")
@click.option("--port", default=None, help="port number")
def cli(dev, solvent, port):
    """
    Protein and ligand trajectory viewer with optimized for
    interactive exploration and bookmarking

    (C) 2025 Bosco Ho
    """
    config.is_dev = dev
    config.is_solvent = solvent
    config.port = port


@cli.command(no_args_is_help=True)
@click.argument("h5")
def traj(h5):
    """
    Open H5
    """
    config.reader_class = "TrajReader"
    config.trajectories = [h5]
    run_server(config)


@cli.command(no_args_is_help=True)
@click.argument("matrix_yaml", default="matrix.yaml", required=False)
@click.option("--mode", default="matrix-strip", required=False)
def matrix(matrix_yaml, mode):
    """
    Open H5 with matrix
    """
    config.reader_class = "MatrixTrajReader"
    config.matrix_yaml = matrix_yaml
    config.mode = mode
    run_server(config)


@cli.command(no_args_is_help=True)
@click.argument("pdb")
@click.argument("sdf")
@click.argument("csv", required=False)
def ligands(pdb, sdf, csv):
    """
    Open PDB with ligands in SDF
    """
    config.reader_class = "LigandsReceptorReader"
    config.pdb = pdb
    config.ligands = sdf
    config.csv = csv
    run_server(config)


@cli.command(no_args_is_help=True)
@click.argument("pdb")
def frame(pdb):
    """
    Open PDB or PARMED
    """
    config.reader_class = "FrameReader"
    config.pdb_or_parmed = pdb
    run_server(config)


@cli.command(no_args_is_help=True)
@click.argument("test_url")
@click.argument("open_url", required=False)
def open_url(test_url, open_url):
    """
    Open OPEN_URL when TEST_URL works
    """
    open_url_in_background(test_url, open_url)


if __name__ == "__main__":
    cli()
