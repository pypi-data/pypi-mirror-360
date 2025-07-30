
import numpy as np
import itertools

from .. import Numputils as nput
from .. import Iterators as itut
from .Permutations import UniquePermutations, UniqueSubsets, IntegerPartitioner, IntegerPartitioner2D

__all__ = [
    "YoungTableauxGenerator"
]

class YoungTableauxGenerator:

    def __init__(self, base_int):
        self.base = base_int
        self.cache = {}

    def get_standard_tableaux(self, partitions=None, *, symbols=None,  brute_force=False, **partition_opts):
        if partitions is None:
            partitions = IntegerPartitioner.partitions(self.base, **partition_opts)
        return [
            self.standard_partition_tableaux(partition, cache=self.cache, brute_force=brute_force, symbols=symbols)
            for partition in partitions
        ]

    @classmethod
    def standard_partition_tableaux_bf(cls, partition, unique_perms=False, concatenate=False):
        if unique_perms:
            n = len(partition)
            perm_list = sum(([n - i] * k for i, k in enumerate(partition)), [])
            #
            perms = UniquePermutations(perm_list[1:]).permutations()
            perms = np.concatenate([
                np.full((len(perms), 1), n, dtype=perms.dtype),
                perms
            ], axis=1)
            idx_pos = np.argsort(np.argsort(-perms, axis=1))
        else:
            idx_pos = nput.permutation_indices(sum(partition), sum(partition))

        tableaux = np.array_split(idx_pos, np.cumsum(partition)[:-1], axis=1)
        valid = np.full(len(idx_pos), True)
        for i, t in enumerate(zip(*tableaux)):
            if any(len(tt) > 1 and (np.diff(tt) < 0).any() for tt in t):
                valid[i] = False
            if valid[i] and any(len(tt) > 1 and (np.diff(tt) < 0).any() for tt in itut.transpose(t)):
                valid[i] = False

        tableaux = [t[valid] for t in tableaux]
        if concatenate:
            tableaux = np.concatenate(tableaux, axis=1)

        # if return_perms:
        #     return perms[valid], tableaux
        # else:
        return tableaux

    @classmethod
    def populate_sst_frames(cls, partition, frame, segment_lists):
        frame_list = []
        for segments in segment_lists:
            splits = [0] * len(partition)
            subframe = [np.zeros(k, dtype=int) for k in partition]
            for s, r in zip(subframe, frame):
                k = 0
                for n, i in enumerate(r):
                    j = splits[n]
                    s[k:k + i] = segments[n][j:j + i]
                    splits[n] += i
                    k += i
            frame_list.append(subframe)
        return frame_list

    @classmethod
    def standard_partitions(cls, partition):
        #TODO: make this more efficient
        base_partitions = IntegerPartitioner2D.get_partitions(partition, partition)
        offsets = np.cumsum(base_partitions, axis=-1)
        valid = np.all(np.all(np.diff(offsets, axis=-2) <= 0, axis=-2), axis=-1)

        return [
            base_partitions[valid,],
            offsets[valid,],
        ]

    @classmethod
    def hook_numbers(cls, partition):
        return [
            (p - j) + sum(
                1 if pk >= (j+1) else 0
                for pk in partition[i + 1:]
            )
            for i, p in enumerate(partition)
            for j in range(p)
        ]

    @classmethod
    def count_standard_tableaux(cls, partition):
        nums = np.arange(1, np.sum(partition)+1)
        denoms = np.sort(cls.hook_numbers(partition))
        return np.round(np.prod(nums/denoms)).astype(int)

    @classmethod
    def split_frame(cls, partition, offsets):  # `offsets` is just a vector of offset indices
        frame_list = []
        mp = np.max(partition)
        partition = np.asanyarray(partition)
        offsets = np.asanyarray(offsets)
        for i in range(len(partition)):
            p = partition[i]
            if p == 0: continue
            o = offsets[i]
            diffs = np.zeros_like(offsets)
            diffs[i + 1:] = o - offsets[i + 1:]
            col_offset = np.full(len(offsets), o)
            this_part = np.clip(partition - diffs, 0, mp)
            frame_list.append([this_part, col_offset])
            partition = np.min([partition, diffs], axis=0)
            offsets = offsets
        return frame_list

    @classmethod
    def _sst_2(cls, partition, cache=None, symbols=None):
        tableaux = None
        if len(partition) == 1:
            tableaux = [
                np.arange(partition[0], dtype=int)[np.newaxis]
            ]
        elif sum(partition) == 2:
            tableaux = [
                np.array([[0]], dtype=int),
                np.array([[1]], dtype=int)
            ]
        elif sum(partition) == 3:
            if partition[0] == 2:
                tableaux = [
                    np.array([[0, 1], [0, 2]], dtype=int),
                    np.array([[2], [1]], dtype=int)
                ]
            else:
                tableaux = [
                    np.array([[0]], dtype=int),
                    np.array([[1]], dtype=int),
                    np.array([[2]], dtype=int),
                ]
        if tableaux is not None:
            if symbols is not None:
                symbols = np.asanyarray(symbols)
                return [
                    symbols[tab]
                    for tab in tableaux
                ]

            return tableaux

        if cache is None:
            cache = {}
        partition = tuple(partition)
        if partition in cache:
            tableaux = cache[partition]
            if symbols is not None:
                symbols = np.asanyarray(symbols)
                return [
                    symbols[tab]
                    for tab in tableaux
                ]

            return tableaux
        else:
            frames, offsets = cls.standard_partitions(partition)
            offsets[:, :, 1:] = offsets[:, :, :-1]
            offsets[:, :, 0] = 0

            if symbols is None:
                symbols = np.arange(np.sum(partition))
            segments = np.array_split(symbols, np.cumsum(partition)[:-1])

            # n_frames = 0
            tableaux_generators = []
            for f, o in zip(frames, offsets):
                # nsubs = 1
                subframes = []
                for pp, oo, seg in zip(f.T, o.T, segments):
                    frame_splits = cls.split_frame(pp, oo)
                    partition_sizes = [
                        np.sum(p) for p, o in frame_splits
                    ]
                    comb_splits = np.array_split(
                        UniqueSubsets.unique_subsets(partition_sizes),
                        partition_sizes[:-1],
                        axis=1
                    )
                    subssts = []
                    for spl in zip(*comb_splits):
                        subrow = []
                        for (p, o), ss in zip(frame_splits, spl):
                            p_idx = [x for x, p0 in enumerate(p) if p0 > 0]
                            subsubssts = cls._sst_2([p[x] for x in p_idx], cache=cache, symbols=seg[ss])
                            reshaped_ssts = []
                            for ss in zip(*subsubssts):
                                p_full = [[]] * len(p)
                                for x, r in zip(p_idx, ss):
                                    p_full[x] = r
                                reshaped_ssts.append([o, p_full])
                            subrow.append(reshaped_ssts)
                        subssts.append(list(itertools.product(*subrow)))
                        # nsubs *= len(subssts[-1])

                    subframes.append(subssts)
                # n_frames += nsubs

                tableaux_generators.append(subframes)

            n_frames = sum(
                np.prod([
                    len(f)
                    for f in frame_list
                ])
                for subframes in tableaux_generators
                for frame_list in itertools.product(*subframes)
            )

            tableaux = [np.zeros((n_frames, p), dtype=int) for p in partition]
            n = 0
            for subframes in tableaux_generators:
                for frame_list in itertools.product(*subframes):
                    for frame_choice in itertools.product(*frame_list):
                        for f in frame_choice:
                            for oo, p_sets in f:
                                for i, (o, ss) in enumerate(zip(oo, p_sets)):
                                    k = len(ss)
                                    if k > 0:
                                        tableaux[i][n, o:o + k] = ss
                        n += 1

            cache[partition] = tableaux

            return tableaux
    @classmethod
    def standard_partition_tableaux(cls, partition, cache=None, symbols=None, brute_force=False):
        if brute_force:
            tableaux = cls.standard_partition_tableaux_bf(partition, concatenate=False, unique_perms=False)
        else:
            tableaux = cls._sst_2(partition, cache=cache)
        if symbols is not None:
            symbols = np.asanyarray(symbols)
            tableaux = [
                symbols[tab]
                for tab in tableaux
            ]
        return tableaux

