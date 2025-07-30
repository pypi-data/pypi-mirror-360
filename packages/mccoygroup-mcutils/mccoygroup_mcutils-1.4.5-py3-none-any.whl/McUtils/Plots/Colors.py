import uuid

import numpy as np
import urllib.parse
from ..Data import ColorData
from .. import Numputils as nput
from .. import Devutils as dev

__all__ = [
    "ColorPalette"
]

#TODO: add ColorSpaces enum for validation

class ColorPalette:
    def __init__(self, colors, blend_spacings=None, lab_colors=None, color_space='rgb', cycle=False):
        if isinstance(colors, str):
            colors = ColorData[colors].data
        if not self.is_palette_list(colors):
            raise ValueError(f"{colors} is not a color palette list")
        self.color_strings, self.lab_colors = self.prep_color_palette(colors, color_space, lab_colors=lab_colors)
        # TODO: add more sophisticated blending
        if blend_spacings is None:
            blend_spacings = np.linspace(0, 1, len(self.color_strings))
        self.abcissae = np.asanyarray(blend_spacings)
        self.cycle = cycle

    def __hash__(self):
        return hash((type(self), self.color_strings))

    @classmethod
    def prep_color_palette(cls, colors, color_space='rgb', lab_colors=None):
        if lab_colors is not None:
            lab_colors = np.asanyarray(lab_colors)
        if isinstance(colors[0], str):
            if color_space != 'rgb':
                raise ValueError(f"only rgb color codes supported (got {colors})")
            color_lists = colors
            rgb_array = np.array([cls.parse_rgb_code(c) for c in colors])
            if lab_colors is None:
                lab_colors = cls.color_convert(rgb_array.T, "rgb", "lab").T
        else:
            colors = np.asanyarray(colors)
            if lab_colors is None:
                if color_space != 'lab':
                    lab_colors = cls.color_convert(colors.T, color_space, "lab").T
                else:
                    lab_colors = colors
            if color_space != 'rgb':
                rgb_colors = cls.color_convert(colors.T, color_space, 'rgb').T
            else:
                rgb_colors = colors
            color_lists = [cls.rgb_code(c, 2) for c in rgb_colors]

        return tuple(color_lists), lab_colors


    @classmethod
    def is_palette_list(self, colors):
        return (
                dev.is_list_like(colors)
                and all(
                    isinstance(c, str)
                    or nput.is_numeric_array_like(c)
                    for c in colors
                )
        )
    def flip(self):
        return type(self)(list(reversed(self.color_strings)))

    def __eq__(self, other):
        if not hasattr(other, "color_strings"): return False
        return self.color_strings == other.color_strings

    def get_colorblindness_test_url(self):
        return "https://davidmathlogic.com/colorblind/#" + "-".join(
            urllib.parse.quote(c[:7] if c.startswith("#") else c[:6]) for c in self.color_strings
        )

    def blend(self, amount, modification_space='lab', rescale=False, return_color_code=True):
        amount = np.asanyarray(amount)
        smol = amount.ndim == 0
        if smol: amount = np.array([amount])
        insertion_indices = np.searchsorted(self.abcissae, amount)
        terminals = insertion_indices == len(self.abcissae)
        starts = insertion_indices == 0
        rems = np.logical_not(np.logical_or(terminals, starts))
        codes = [""] * len(amount)
        new_colors = np.empty((len(amount), len(self.lab_colors[0])), dtype=float)
        if return_color_code:
            term_pos = np.where(terminals)
            if len(term_pos) > 0:
                for i in term_pos[0]:
                    codes[i] = self.color_strings[-1]
            start_pos = np.where(starts)
            if len(start_pos) > 0:
                for i in start_pos[0]:
                    codes[i] = self.color_strings[0]
        else:
            if terminals.any():
                color = np.array(self.parse_rgb_code(self.color_strings[-1]))
                new_colors[terminals] = color[np.newaxis]
            if starts.any():
                color = np.array(self.parse_rgb_code(self.color_strings[0]))
                new_colors[starts] = color[np.newaxis]
        if rems.any():
            rem_inds = insertion_indices[rems]
            x = self.abcissae[rem_inds - 1,]
            y = self.abcissae[rem_inds,]
            d = ((amount[rems,] - x) / (y - x))[:, np.newaxis]

            colors = self.lab_colors
            if modification_space != 'lab':
                colors = self.color_convert(colors, 'lab', modification_space).T
            new_lab = colors[rem_inds - 1,] * (1 - d) + colors[rem_inds,] * d
            rgb = self.color_convert(new_lab.T, modification_space, 'rgb').T

            if return_color_code:
                rgb = self.rgb_code(rgb.T)
                rems = np.where(rems)[0]
                for n,r in enumerate(rgb):
                    codes[rems[n]] = r
            else:
                new_colors[rems,] = rgb

        if return_color_code:
            if smol: codes = codes[0]
            return codes
        else:
            if rescale: new_colors = self.color_rescale(new_colors, 'rgb')
            if smol: new_colors = new_colors[0]
            return new_colors

    def as_colormap(self, levels=None, cmap_type='list', name=None, **opts):
        from matplotlib.colors import ListedColormap, LinearSegmentedColormap

        if levels is None:
            levels = np.linspace(0, 1, len(self.color_strings))
            vals = np.array(self.parse_rgb_code(self.color_strings)) / 255
        else:
            if nput.is_int(levels):
                levels = np.linspace(0, 1, levels)
            vals = self(levels)

        if dev.str_is(cmap_type, 'list'):
            cmap = np.concatenate([
                vals,
                np.ones((len(vals), 1)),
                ],
                axis=1
            )
            new_map = ListedColormap(cmap, **opts)
        elif dev.str_is(cmap_type, 'interpolated'):
            cmap_dict = {
                'red':np.concatenate([
                    levels[:, np.newaxis],
                    vals[:, (0,)],
                    vals[:, (0,)]
                ],axis=1),
                'green':np.concatenate([
                    levels[:, np.newaxis],
                    vals[:, (1,)],
                    vals[:, (1,)]
                ],axis=1),
                'blue':np.concatenate([
                    levels[:, np.newaxis],
                    vals[:, (2,)],
                    vals[:, (2,)]
                ],axis=1)
            }
            if name is None:
                name = '-'.join(['cmap']+str(uuid.uuid4()).split("-")[:2])
            new_map = LinearSegmentedColormap(name, segmentdata=cmap_dict, **opts)
        else:
            new_map: ListedColormap|LinearSegmentedColormap = cmap_type(levels, vals, **opts)

        return new_map

    def __call__(self, amount, rescale=True, return_color_code=False):
        return self.blend(amount, rescale=rescale, return_color_code=return_color_code)

    @classmethod
    def color_normalize(cls, color_list, color_space='rgb'):
        color_list = np.asanyarray(color_list)
        smol = color_list.ndim == 1
        if smol: color_list = color_list[:, np.newaxis]
        if color_space == 'rgb':
            color_list = np.clip(color_list, 0, 255)
        elif color_space == 'xyz':
            color_list = np.clip(color_list, 0, 100)
        elif color_list in {'hsl', 'hsv'}:
            color_list = np.clip(color_list, 0, 1)
        if smol: color_list = color_list[:, 0]
        return color_list

    @classmethod
    def color_rescale(cls, color_list, color_space='rgb'):
        color_list = np.asanyarray(color_list)
        if color_space == 'rgb':
            color_list = color_list / 255
        elif color_space == 'xyz':
            color_list = color_list / 100
        return color_list
    @classmethod
    def color_modify(cls, color, modification_function, color_space='rgb', modification_space='lab', clip=True):
        as_code = isinstance(color, str)
        padding = 2
        if as_code:
            if color_space != 'rgb':
                raise ValueError(f"only rgb color codes supported (got {color})")
            color, padding = cls.parse_rgb_code(color, return_padding=True)
        if color_space != modification_space:
            lab_color = cls.color_convert(color, color_space, modification_space)
        else:
            lab_color = color
        lab_color = modification_function(*lab_color)
        if color_space != modification_space:
            color = cls.color_convert(lab_color, modification_space, color_space)
        if clip:
            color = cls.color_normalize(color, color_space)

        if as_code:
            color = cls.rgb_code(color, padding=padding)
        return color
    @classmethod
    def color_lighten(cls, color, percentage,
                      color_space='rgb',
                      modification_space='lab',
                      shift=False,
                      absolute=False, clip=True):
        if modification_space == 'lab':
            if shift:
                percentage = 100*percentage
                conversion = lambda l,a,b:[l+percentage, a, b]
            elif absolute:
                percentage = 100*percentage
                conversion = lambda l,a,b:[percentage, a, b]
            else:
                conversion = lambda l,a,b:[l*(1+percentage), a, b]
        elif modification_space in {'hsv', 'hsl'}:
            if shift:
                conversion = lambda h,s,l:[h, s, l+percentage]
            elif absolute:
                conversion = lambda h,s,l:[h, s, percentage]
            else:
                conversion = lambda h,s,l:[h, s, l*(1+percentage)]
        else:
            raise ValueError(f"can't lighten color in modification_space `{modification_space}`")

        return cls.color_modify(color, conversion, color_space=color_space, modification_space=modification_space, clip=clip)

    def __len__(self):
        return len(self.color_strings)
    def __getitem__(self, item):
        if nput.is_int(item):
            if not self.cycle:
                return self.color_strings[item]
            else:
                return self.color_strings[item % len(self.color_strings)]
        else:
            return type(self)(
                self.color_strings[item],
                blend_spacings=self.abcissae[item],
                lab_colors=self.lab_colors[item]
            )


    @classmethod
    def rgb_code(cls, rgb, padding=2):
        if not isinstance(rgb[0], (int, float, np.floating, np.integer)):
            return [
                cls.rgb_code([r, g, b])
                for r, g, b in zip(*rgb)
            ]
        rgb = np.round(rgb).astype(int)
        return f"#{rgb[0]:0>{padding}x}{rgb[1]:0>{padding}x}{rgb[2]:0>{padding}x}"
    @classmethod
    def parse_rgb_code(cls, code, padding=None, return_padding=False):
        if not isinstance(code, str):
            if not return_padding:
                return [
                    cls.parse_rgb_code(c, padding=padding, return_padding=False)
                    for c in code
                ]
            else:
                padding, _ = cls.parse_rgb_code(code[0], padding=padding, return_padding=True)
                return [
                    cls.parse_rgb_code(c, padding=padding, return_padding=False)
                    for c in code
                ], padding
        if code[0] == "#":
            code = code[1:]
        if padding is None:
            padding = len(code) // 3
        color_list = [
            int(code[(padding*i):(padding*(i+1))], 16)
            for i in range(3)
        ]
        if return_padding:
            return color_list, padding
        else:
            return color_list

    converters = {}
    @classmethod
    def color_convert(self, color, original_space, target_space):
        if (original_space, target_space) in self.converters:
            conversion = self.converters[(original_space, target_space)]
        else:
            try:
                conversion = getattr(self, f"{original_space}_to_{target_space}") #TODO: register these better
            except AttributeError:
                # send everything through RGB
                conversion1 = getattr(self, f"{original_space}_to_rgb")
                conversion2 = getattr(self, f"rgb_to_{target_space}")
                conversion = lambda *c: conversion2(*conversion1(*c))
        return conversion(*color)

    xyz_to_rbg_array = [
        [ 3.2406, -1.5372, -0.4986],
        [-0.9689,  1.8758,  0.0415],
        [ 0.0557, -0.2040,  1.0570],
    ]
    @classmethod
    def xyz_to_rgb(self, x, y, z):
        # converted from https://www.easyrgb.com/en/math.php
        if not isinstance(self.xyz_to_rbg_array, np.ndarray):
            self.xyz_to_rbg_array = np.array(self.xyz_to_rbg_array)

        xyz = np.array([x, y, z]) / 100
        rgb = np.dot(self.xyz_to_rbg_array, xyz)
        mask = rgb > 0.0031308
        rgb[mask] = 1.055*rgb[mask]**(1/2.4) - 0.055
        not_mask = np.logical_not(mask)
        rgb[not_mask] = rgb[not_mask] * 12.92
        return rgb * 255

    rgb_to_xyz_array = [ # just the inverse
        [0.4124, 0.3576, 0.1805],
        [0.2126, 0.7152, 0.0722],
        [0.0193, 0.1192, 0.9505],
    ]
    @classmethod
    def rgb_to_xyz(self, r, g, b):
        if not isinstance(self.rgb_to_xyz_array, np.ndarray):
            self.rgb_to_xyz_array = np.array(self.rgb_to_xyz_array)

        rgb = np.array([r, g, b]) / 255
        mask = rgb > 0.04045
        rgb[mask] = ((rgb[mask] + 0.055) / 1.055)**(2.4)
        not_mask = np.logical_not(mask)
        rgb[not_mask] = rgb[not_mask] / 12.92

        xyz = np.dot(self.rgb_to_xyz_array, rgb)
        return xyz * 100

    @classmethod
    def _rgb2hue(cls, rgb, diff, max_val):

        diff_r, diff_g, diff_b = [
            ((max_val - c) / 6 + (diff / 2)) / diff
            for c in rgb
        ]
        r_primary, g_primary, b_primary = [
            max_val == c
            for c in rgb
        ]

        h = np.zeros_like(diff)
        h[r_primary] = (diff_b - diff_g)
        h[g_primary] = (1 / 3 + diff_r - diff_b)
        h[b_primary] = (2 / 3 + diff_g - diff_r)

        h[h < 0] += 1
        h[h > 1] -= 1

        return h
    @classmethod
    def rgb_to_hsl(self, r, g, b):

        rgb = np.array([r, g, b]) / 255
        smol = rgb.ndim == 1
        if smol:
            rgb = rgb[:, np.newaxis]

        min_val = np.min(rgb, axis=0)
        max_val = np.max(rgb, axis=0)
        diff = max_val - min_val

        L = (max_val + min_val) / 2

        non_gray = diff > 0
        s = np.zeros_like(L)
        h = np.zeros_like(L)
        if non_gray.any():
            s[non_gray] = (diff / (2 - (max_val + min_val)))
            dim_mask = np.logical_and(non_gray, L < .5)
            s[dim_mask] = (diff / (max_val + min_val))[dim_mask]

            h_ = self._rgb2hue(rgb[:, non_gray], diff[non_gray], max_val[non_gray])
            h[non_gray] = h_

        hsl = np.array([h, s, L])
        if smol:
            hsl = hsl[:, 0]

        return hsl

    @classmethod
    def _hue2rgb(cls, v1, v2, h):

        h = np.array(h)
        v1 = np.array(v1)
        v2 = np.array(v2)
        h[h < 0] += 1
        h[h > 1] -= 1

        res = v1.copy()
        mask = 6*h < 1
        res[mask] = v1[mask] + (v2[mask] - v1[mask]) * 6*h[mask]
        rem = np.logical_not(mask)
        mask = np.logical_and(rem, 2*h < 1)
        res[mask] = v2[mask]
        rem = np.logical_and(rem, np.logical_not(mask))
        mask = np.logical_and(rem, 3*h < 2)
        res[mask] = v1[mask] + (v2[mask] - v1[mask]) * 6*(2/3 - h[mask])

        return res

    @classmethod
    def hsl_to_rgb(cls, h, s, l):

        hsl = np.array([h, s, l])
        smol = hsl.ndim == 1
        if smol:
            hsl = hsl[:, np.newaxis]
        non_gray = hsl[1] > 0
        dim = np.logical_and(non_gray, hsl[2] < .5)

        rgb = np.zeros_like(hsl)
        if non_gray.any():
            h, s, L = hsl
            v2 = np.zeros_like(h)
            v2[non_gray] = ((L + s) - (s * L))[non_gray]
            v2[dim] = (L * (1 + s))[dim]

            v1 = np.zeros_like(h)
            v1[non_gray] = 2 * L[non_gray] - v2[non_gray]

            for i,shift in enumerate([1/3, 0, -1/3]):
                rgb[i, non_gray] = cls._hue2rgb(v1[non_gray], v2[non_gray], h[non_gray] + shift)

        if smol:
            rgb = rgb[:, 0]

        return rgb * 255

    @classmethod
    def rgb_to_hsv(self, r, g, b):

        rgb = np.array([r, g, b]) / 255
        smol = rgb.ndim == 1
        if smol:
            rgb = rgb[:, np.newaxis]

        min_val = np.min(rgb, axis=0)
        max_val = np.max(rgb, axis=0)
        diff = max_val - min_val

        v = max_val

        non_gray = diff > 0
        s = np.zeros_like(v)
        h = np.zeros_like(v)
        if non_gray.any():
            s[non_gray] = (diff / max_val)[non_gray]
            h_ = self._rgb2hue(rgb[:, non_gray], diff[non_gray], max_val[non_gray])
            h[non_gray] = h_

        hsl = np.array([h, s, v])
        if smol:
            hsl = hsl[:, 0]

        return hsl

    @classmethod
    def hsv_to_hsl(cls, h, s, v):

        hsv = np.array([h, s, v])
        smol = hsv.ndim == 1
        if smol:
            hsv = hsv[:, np.newaxis]

        h, s, v = hsv
        max_val = np.array(v)
        diff = max_val * np.array(s)
        min_val = max_val - diff

        L = (max_val + min_val) / 2

        non_gray = diff > 0
        s = np.zeros_like(L)
        if non_gray.any():
            s[non_gray] = (diff / (2 - (max_val + min_val)))
            dim_mask = np.logical_and(non_gray, L < .5)
            s[dim_mask] = (diff / (max_val + min_val))[dim_mask]

        hsl = np.array([h, s, L])
        if smol:
            hsl = hsl[:, 0]

        return hsl

    @classmethod
    def hsv_to_rgb(cls, h, s, v):
        return cls.hsl_to_rgb(*cls.hsv_to_hsl(h, s, v))

    lab_scaling_reference = [95.0489, 100.0, 108.8840]
    @classmethod
    def xyz_to_lab(cls, x, y, z, scaling=None):

        xyz = np.array([x, y, z])
        smol = xyz.ndim == 1
        if smol:
            xyz = xyz[:, np.newaxis]

        if scaling is None:
            scaling = cls.lab_scaling_reference

        xyz /= np.array(scaling)[:, np.newaxis]

        mask = xyz > 0.008856
        xyz[mask] = xyz[mask] ** (1/3)
        not_max = np.logical_not(mask)
        xyz[not_max] = (7.787 * xyz[not_max]) + (16/116)

        L = 116 * xyz[1] - 16
        a = 500 * (xyz[0] - xyz[1])
        b = 200 * (xyz[1] - xyz[2])

        lab = np.array([L, a, b])
        if smol:
            lab = lab[:, 0]

        return lab

    @classmethod
    def lab_to_xyz(cls, l, a, b, scaling=None):

        lab = np.array([l, a, b])
        smol = lab.ndim == 1
        if smol:
            lab = lab[:, np.newaxis]

        if scaling is None:
            scaling = cls.lab_scaling_reference

        y = (lab[0] + 16) / 116
        x = lab[1] / 500 + y
        z = y - lab[2] / 200

        xyz = np.array([x, y, z])

        mask = xyz**3 > 0.008856
        xyz[mask] = xyz[mask] ** (3)
        not_max = np.logical_not(mask)
        xyz[not_max] = (xyz[not_max] - (16/116)) / 7.787

        xyz *= np.array(scaling)[:, np.newaxis]
        if smol:
            xyz = xyz[:, 0]

        return xyz

    @classmethod
    def rgb_to_lab(cls, r, g, b, xyz_scaling=None):
        return cls.xyz_to_lab(*cls.rgb_to_xyz(r, g, b), scaling=xyz_scaling)
    @classmethod
    def lab_to_rgb(cls, l, a, b, xyz_scaling=None):
        return cls.xyz_to_rgb(*cls.lab_to_xyz(l, a, b, scaling=xyz_scaling))