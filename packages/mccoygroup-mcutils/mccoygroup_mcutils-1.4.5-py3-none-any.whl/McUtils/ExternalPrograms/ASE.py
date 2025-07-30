

__all__ = [
    "ASEMolecule"
]

import sys

import numpy as np, io, os
from .. import Numputils as nput

from .ExternalMolecule import ExternalMolecule
from .ChemToolkits import ASEInterface

class ASEMolecule(ExternalMolecule):
    """
    A simple interchange format for ASE molecules
    """

    @property
    def atoms(self):
        return self.mol.symbols
    @property
    def coords(self):
        return self.mol.positions
    @property
    def charges(self):
        return self.mol.charges

    @classmethod
    def from_coords(cls, atoms, coords, charge=None, calculator=None, **etc):
        if calculator is not None and charge is not None:
            calculator.set_charge(charge)

        return cls(
            ASEInterface.Atoms(
                atoms,
                coords,
                calculator=calculator,
                **etc
            )
        )

    @classmethod
    def from_mol(cls, mol, coord_unit="Angstroms", calculator=None):
        from ..Data import UnitsData

        return cls.from_coords(
            mol.atoms,
            mol.coords * UnitsData.convert(coord_unit, "Angstroms"),
            # bonds=mol.bonds,
            charge=mol.charge,
            calculator=calculator
        )

    # def calculate_gradient(self, geoms=None, force_field_generator=None, force_field_type='mmff'):
    #     if force_field_generator is None:
    #         force_field_generator = self.get_force_field
    #     cur_geom = np.array(self.mol.GetPositions()).reshape(-1, 3)
    #     if geoms is not None:
    #         geoms = np.asanyarray(geoms)
    #         base_shape = geoms.shape[:-2]
    #         geoms = geoms.reshape((-1,) + cur_geom.shape)
    #         vals = np.empty((len(geoms), np.prod(cur_geom.shape, dtype=int)), dtype=float)
    #         try:
    #             for i, g in enumerate(geoms):
    #                 self.mol.SetPositions(g)
    #                 ff = force_field_generator(force_field_type)
    #                 vals[i] = ff.CalcGrad()
    #         finally:
    #             self.mol.SetPositions(cur_geom)
    #         return vals.reshape(base_shape + (-1,))
    #     else:
    #         ff = force_field_generator(force_field_type)
    #         return np.array(ff.CalcGrad()).reshape(-1)

    # def get_calculator(self):
    #     if isinstance(self.calc, MassWeightedCalculator):
    #         return self.calc.copy()
    #     else:
    #         return self.load_class()(self.calc.base_calc)

    def calculate_energy(self, geoms=None, order=None, calc=None):
        if calc is None:
            calc = self.mol.calc
        just_eng = order is None
        if just_eng: order = 0
        props = ['energy']
        if order > 0:
            props.append('forces')
        if order > 1:
            raise ValueError("ASE calculators only need to implement forces")
        if geoms is None:
            calc.calculate(self.mol, props)
            res = [
                calc.results[k]
                for k in props
            ]
            if order > 0:
                res[1] *= -1
        else:
            cur_geom = self.mol.positions
            geoms = np.asanyarray(geoms)
            base_shape = geoms.shape[:-2]
            geoms = geoms.reshape((-1,) + cur_geom.shape)
            engs = np.empty((len(geoms),), dtype=float)
            if order > 0:
                grads = np.empty((len(geoms), np.prod(cur_geom.shape, dtype=int)), dtype=float)
            else:
                grads = None
            try:
                for i, g in enumerate(geoms):
                    self.mol.positions = g
                    calc.calculate(self.mol, props)
                    vals = [
                        calc.results[k]
                        for k in props
                    ]
                    engs[i] = vals[0]
                    if order > 0:
                        grads[i] = -vals[1]
            finally:
                self.mol.positions = cur_geom
            res = [engs]
            if order > 0:
                res.append(grads)
        if just_eng:
            res = res[0]
        return res


    convergence_criterion = 1e-4
    max_steps = 100
    def optimize_structure(self, geoms=None, calc=None, quiet=True, logfile=None, fmax=None, steps=None, **opts):
        BFGS = ASEInterface.submodule('optimize').BFGS

        if logfile is None:
            if quiet:
                logfile = io.StringIO()
            else:
                logfile = sys.stdout

        if calc is None:
            calc = self.mol.calc
        cur_calc = self.mol.calc
        cur_geom = self.mol.positions
        try:
            self.mol.calc = calc
            if geoms is None:
                opt_rea = BFGS(self.mol, logfile=logfile, **opts)
                if fmax is None:
                    fmax = self.convergence_criterion
                if steps is None:
                    steps = self.max_steps
                opt = opt_rea.run(fmax=fmax, steps=steps)
                opt_coords = self.mol.positions
            else:
                cur_geom = self.mol.positions
                geoms = np.asanyarray(geoms)
                base_shape = geoms.shape[:-2]
                geoms = geoms.reshape((-1,) + cur_geom.shape)
                opt = np.empty((len(geoms),), dtype=object)
                opt_coords = np.empty_like(geoms)

                for i, g in enumerate(geoms):
                    self.mol.positions = g
                    opt_rea = BFGS(self.mol, logfile=logfile, **opts)
                    if fmax is None:
                        fmax = self.convergence_criterion
                    if steps is None:
                        steps = self.max_steps
                    opt[i] = opt_rea.run(fmax=fmax, steps=steps)
                    opt_coords[i] = self.mol.positions
                opt = opt.reshape(base_shape)
                opt_coords = opt_coords.reshape(base_shape + opt_coords.shape[1:])
        finally:
            self.mol.calc = cur_calc
            self.mol.positions = cur_geom

        return opt, opt_coords, {}