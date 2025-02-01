from .volume import Volume

class Nifti:
    def __init__(self, data=None, modalities=None):
        self.data = data
        self.volumes = []
        self.shape = data.shape if data is not None else None
        self.num_volumes = 0
        self.modalities = modalities if modalities is not None else []
        if data is not None:
            for modality_index in range(data.shape[3]):
                modality_data = data[:, :, :, modality_index]
                for axis in ['x', 'y', 'z']:
                    volume = Volume(modality_data, axis)
                    self.add_volume(volume)

    def add_volume(self, volume):
        self.volumes.append(volume)
        self.num_volumes += 1

    def get_volume(self, index):
        return self.volumes[index]

    def get_volumes(self):
        return self.volumes

    def __getitem__(self, index):
        return self.get_volume(index)

    def __eq__(self, other):
        return self.shape == other.shape and self.num_volumes == other.num_volumes and self.modalities == other.modalities

    def __repr__(self):
        return f"Nifti(shape={self.shape}, num_volumes={self.num_volumes}, modalities={self.modalities})"