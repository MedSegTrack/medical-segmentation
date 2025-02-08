from .voxel import Voxel

class Slice:
    def __init__(self, data, z_index, axis):
        self.data = data
        self.z_index = z_index
        self.axis = axis
        if axis == 'x':
            self.shape = (data.shape[1], data.shape[2])
        elif axis == 'y':
            self.shape = (data.shape[0], data.shape[2])
        elif axis == 'z':
            self.shape = (data.shape[0], data.shape[1])
        else:
            raise ValueError("Invalid axis")

    def get_voxel(self, x, y):
        if self.axis == 'x':
            return Voxel(self.data, self.z_index, x, y)
        elif self.axis == 'y':
            return Voxel(self.data, x, self.z_index, y)
        elif self.axis == 'z':
            return Voxel(self.data, x, y, self.z_index)
        else:
            raise ValueError("Invalid axis")

    def get_image_as_array(self):
        if self.axis == 'x':
            return self.data[self.z_index, :, :]
        elif self.axis == 'y':
            return self.data[:, self.z_index, :]
        elif self.axis == 'z':
            return self.data[:, :, self.z_index]
        else:
            raise ValueError("Invalid axis")

    def __eq__(self, other):
        return self.z_index == other.z_index and (self.get_image_as_array() == other.get_image_as_array()).all()

    def __repr__(self):
        return f"Slice(z_index={self.z_index}, shape={self.shape}, axis={self.axis})"