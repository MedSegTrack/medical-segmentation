from .slice import Slice

class Volume:
    def __init__(self, data, axis, modality):
        self.data = data
        self.axis = axis
        self.modality = modality
        self.shape = data.shape

    def get_slice(self, index):
        return Slice(self.data, index, self.axis)

    def __getitem__(self, index):
        return self.get_slice(index)

    def __eq__(self, other):
        return self.axis == other.axis and self.shape == other.shape

    def __repr__(self):
        return f"Volume(axis={self.axis}, shape={self.shape}, modality={self.modality})"