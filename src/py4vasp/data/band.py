import functools
import itertools
import numpy as np
import plotly.graph_objects as go
from .projectors import Projectors


class Band:
    def __init__(self, raw_band):
        self._raw = raw_band
        self._fermi_energy = raw_band.fermi_energy
        self._kpoints = raw_band.kpoints
        self._bands = raw_band.eigenvalues
        self._spin_polarized = len(self._bands) == 2
        scale = raw_band.cell.scale
        lattice_vectors = raw_band.cell.lattice_vectors
        self._cell = scale * np.array(lattice_vectors)
        self._line_length = np.array(raw_band.line_length)
        self._num_lines = len(self._kpoints) // self._line_length
        self._indices = raw_band.label_indices
        self._labels = raw_band.labels
        if raw_band.projectors is not None:
            self._projectors = Projectors(raw_band.projectors)
        self._projections = raw_band.projections

    @classmethod
    def from_file(cls, file):
        return cls(file.band())

    def read(self, selection=None):
        kpoints = self._kpoints[:]
        return {
            "kpoints": kpoints,
            "kpoint_distances": self._kpoint_distances(kpoints),
            "kpoint_labels": self._kpoint_labels(),
            "fermi_energy": self._fermi_energy,
            **self._shift_bands_by_fermi_energy(),
            "projections": self._read_projections(selection),
        }

    def plot(self, selection=None, width=0.5):
        kdists = self._kpoint_distances(self._kpoints[:])
        fatband_kdists = np.concatenate((kdists, np.flip(kdists)))
        bands = self._shift_bands_by_fermi_energy()
        projections = self._read_projections(selection)
        ticks = [*kdists[:: self._line_length], kdists[-1]]
        labels = self._ticklabels()
        data = []
        for key, lines in bands.items():
            if len(projections) == 0:
                data.append(self._scatter(key, kdists, lines))
            for name, proj in projections.items():
                if self._spin_polarized and not key in name:
                    continue
                upper = lines + width * proj
                lower = lines - width * proj
                fatband_lines = np.concatenate((lower, np.flip(upper, axis=0)), axis=0)
                plot = self._scatter(name, fatband_kdists, fatband_lines)
                plot.fill = "toself"
                plot.mode = "none"
                data.append(plot)
        default = {
            "xaxis": {"tickmode": "array", "tickvals": ticks, "ticktext": labels},
            "yaxis": {"title": {"text": "Energy (eV)"}},
        }
        return go.Figure(data=data, layout=default)

    def _shift_bands_by_fermi_energy(self):
        if self._spin_polarized:
            return {
                "up": self._bands[0] - self._fermi_energy,
                "down": self._bands[1] - self._fermi_energy,
            }
        else:
            return {"bands": self._bands[0] - self._fermi_energy}

    def _scatter(self, name, kdists, lines):
        # insert NaN to split separate lines
        num_bands = lines.shape[-1]
        kdists = np.tile([*kdists, np.NaN], num_bands)
        lines = np.append(lines, [np.repeat(np.NaN, num_bands)], axis=0)
        return go.Scatter(x=kdists, y=lines.flatten(order="F"), name=name)

    def _kpoint_distances(self, kpoints):
        cartesian_kpoints = np.linalg.solve(self._cell, kpoints.T).T
        kpoint_lines = np.split(cartesian_kpoints, self._num_lines)
        kpoint_norms = [np.linalg.norm(line - line[0], axis=1) for line in kpoint_lines]
        concatenate_distances = lambda current, addition: (
            np.concatenate((current, addition + current[-1]))
        )
        return functools.reduce(concatenate_distances, kpoint_norms)

    def _read_projections(self, selection):
        if selection is None:
            return {}
        return self._read_elements(selection)

    def _read_elements(self, selection):
        res = {}
        for select in self._projectors.parse_selection(selection):
            atom, orbital, spin = self._projectors.select(*select)
            label = self._merge_labels([atom.label, orbital.label, spin.label])
            index = (spin.indices, atom.indices, orbital.indices)
            res[label] = self._read_element(index)
        return res

    def _merge_labels(self, labels):
        return "_".join(filter(None, labels))

    def _read_element(self, index):
        sum_weight = lambda weight, i: weight + self._projections[i]
        zero_weight = np.zeros(self._bands.shape[1:])
        return functools.reduce(sum_weight, itertools.product(*index), zero_weight)

    def _kpoint_labels(self):
        if len(self._labels) == 0:
            return None
        # convert from input kpoint list to full list
        labels = np.zeros(len(self._kpoints), dtype=self._labels.dtype)
        indices = np.array(self._indices)
        indices = self._line_length * (indices // 2) + indices % 2 - 1
        labels[indices] = self._labels
        return [l.decode().strip() for l in labels]

    def _ticklabels(self):
        labels = [" "] * (self._num_lines + 1)
        for index, label in zip(self._indices, self._labels):
            i = index // 2  # line has 2 ends
            label = label.decode().strip()
            labels[i] = (labels[i] + "|" + label) if labels[i].strip() else label
        return labels