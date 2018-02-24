from .. import pointdata
from .. import vlr
from ..header import rawheader


def scale_dimension(array_dim, scale, offset):
    return (array_dim * scale) + offset


class LasBase(object):
    def __init__(self, header=None, vlrs=None, points=None):
        self.__dict__['header'] = header if header is not None else rawheader.RawHeader()
        self.__dict__['vlrs'] = vlrs if vlrs is not None else vlr.VLRList()
        if points is not None:
            if isinstance(points, pointdata.NumpyPointData):
                self.__dict__['points_data'] = points
            else:
                self.__dict__['points_data'] = pointdata.NumpyPointData(points)
                self.header.point_data_format_id = self.points_data.point_format_id
        else:
            self.__dict__['points_data'] = pointdata.NumpyPointData.empty(self.header.point_data_format_id)

    @property
    def x(self):
        return scale_dimension(self.X, self.header.x_scale, self.header.x_offset)

    @property
    def y(self):
        return scale_dimension(self.Y, self.header.y_scale, self.header.y_offset)

    @property
    def z(self):
        return scale_dimension(self.Z, self.header.z_scale, self.header.z_offset)

    @property
    def points(self):
        return self.points_data.array

    @points.setter
    def points(self, value):
        self.points_data = pointdata.NumpyPointData(value)

    def __getitem__(self, item):
        return self.points_data[item]

    def __setitem__(self, key, value):
        self.points_data[key] = value

    def __getattr__(self, item):
        return self.points_data[item]

    def __setattr__(self, key, value):
        # try to set directly the dimension in the numpy array
        # if it does not exists, search for an existing property-setter
        try:
            self.points_data[key] = value
        except ValueError as e:
            prop = getattr(self.__class__, key, None)
            if prop is not None and isinstance(prop, property):
                if prop.fset is None:
                    raise AttributeError("Cannot set {}".format(key))
                prop.fset(self, value)
            else:
                super().__setattr__(key, value)

    def update_header(self):
        self.header.point_data_format_id = self.points_data.point_format_id
        self.header.number_of_point_records = len(self.points_data)
        self.header.number_of_points_records_ = len(self.points_data)
        self.header.point_data_record_length = self.points_data.point_size

        self.header.x_max = self.X.max()
        self.header.y_max = self.Y.max()
        self.header.z_max = self.Z.max()

        self.header.x_min = self.X.min()
        self.header.y_min = self.Y.min()
        self.header.z_min = self.Z.min()
