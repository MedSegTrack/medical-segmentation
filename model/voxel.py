class Voxel:
    def __init__(self, data, x, y, z):
        self.data = data
        self.x = x
        self.y = y
        self.z = z
    
    @property
    def value(self):
        return self.data[self.x, self.y, self.z]
    
    @value.setter
    def value(self, new_value):
        self.data[self.x, self.y, self.z] = new_value

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return f"Voxel(x={self.x}, y={self.y}, z={self.z})"