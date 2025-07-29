import logging

import numpy as np

from . import alphaspace2 as as2

logger = logging.getLogger(__name__)


class AlphaSpace:
    def __init__(self, mdtraj):
        # Run the snapshot object by feeding it receptor and binder mdtraj objects.

        self.mdtraj = mdtraj
        self.pocket_calculator = as2.Snapshot()
        self.pocket_calculator.beta_cluster_dist = 1.6
        self.pocket_calculator.contact_cutoff = 1.6
        self.pocket_calculator.pocket_cluster_dist = 4.7
        self.elements = [f"{i + 1}" for i in range(24)]
        self.pockets = []
        self.communities = []

        self.find_pockets()
        self.find_communities()

    def find_pockets(self):
        self.pocket_calculator.run(receptor=self.mdtraj)
        self.pockets = list(self.pocket_calculator.pockets)

    def find_communities(self):
        space_by_i_pocket = {}
        coords_by_i_pocket = {}
        contact_by_i_pocket = {}
        score_by_i_pocket = {}
        centroids_by_i_pocket = {}
        for i, pocket in enumerate(self.pockets):
            coords_by_i_pocket[i] = [list(b.xyz) for b in pocket.betas]
            score_by_i_pocket[i] = np.array([np.min(b.scores) for b in pocket.betas])
            space_by_i_pocket[i] = np.array([b.space for b in pocket.betas])
            contact_by_i_pocket[i] = list(pocket.lining_atoms_idx)
            centroids_by_i_pocket[i] = pocket.centroid

        from .alphaspace2.Community import genCommunityPocket

        communities = genCommunityPocket(
            self.mdtraj.xyz[0] * 10,  ### change nm to Angstrom
            centroids_by_i_pocket,
            space_by_i_pocket,
            contact_by_i_pocket,
            score_by_i_pocket,
            corecut=100,
            auxcut=30,
            tight_option=True,
            tight_cutoff_core=8.5,
            tight_cutoff_aux=6.5,
        )

        self.communities = sorted(communities.values(), key=lambda c: -c["space"])

    @staticmethod
    def gen_pdb_line(
        i_atom,
        atom_name,
        res_name,
        i_res,
        chain_name,
        bfactor,
        element,
        xyz,
        occupancy=0,
    ):
        line = "%6s%5s %4s %-4s%1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s" % (
            "HETATM",
            i_atom % 100000,
            atom_name,
            res_name,
            chain_name,
            i_res % 10000,
            " ",
            xyz[0],
            xyz[1],
            xyz[2],
            bfactor,
            occupancy,
            element,
        )
        return line

    def get_community_pdb_lines(self):
        result = []
        i_atom = self.mdtraj.xyz.shape[1]
        i_res = len(list(self.mdtraj.top.residues))
        for community in self.communities:
            i_pockets = community["core_pockets"]  # + community["aux_pockets"]
            nonpolar_spaces = [self.pockets[i].nonpolar_space for i in i_pockets]
            community["key"] = sum(nonpolar_spaces)
        self.communities.sort(key=lambda c: -c["key"])
        for i_community, community in enumerate(self.communities):
            element = self.elements[i_community % len(self.elements)]
            i_pockets = community["core_pockets"]  # + community["aux_pockets"]
            for i_pocket in i_pockets:
                for alpha in self.pockets[i_pocket].alphas:
                    line = self.gen_pdb_line(
                        i_atom,
                        atom_name=f"P{i_community + 1}",
                        res_name="XXX",
                        i_res=i_res,
                        chain_name=" ",
                        bfactor=i_community,
                        occupancy=community["key"],
                        element=element,
                        xyz=alpha.xyz,
                    )
                    result.append(line)
                    i_atom += 1
            i_res += 1
        logger.info(f"Generated {len(result)} lines of PDB.")
        return result

    def get_pocket_pdb_lines(self):
        result = []
        i_atom = self.mdtraj.xyz.shape[1]
        i_res = len(list(self.mdtraj.top.residues))
        self.pockets.sort(key=lambda p: -p.nonpolar_space)
        for i_pocket, pocket in enumerate(self.pockets):
            element = self.elements[i_pocket % len(self.elements)]
            for alpha in pocket.alphas:
                line = self.gen_pdb_line(
                    i_atom,
                    atom_name=f"P{i_pocket + 1}",
                    res_name="XXX",
                    i_res=i_res,
                    chain_name=" ",
                    bfactor=i_pocket,
                    occupancy=pocket.nonpolar_space,
                    element=element,
                    xyz=alpha.xyz,
                )
                result.append(line)
                i_atom += 1
            i_res += 1
        logger.info(f"Generated {len(result)} lines of PDB.")
        return result
