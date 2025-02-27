from osgeo import gdal


def singleton(cls):
    _instance_dict = {}

    def inner(*args, **kwargs):
        if cls not in _instance_dict:
            _instance_dict[cls] = cls(*args, **kwargs)
        return _instance_dict.get(cls)

    return inner


@singleton
class elevation_utils:
    def __init__(self, tif_path):
        self.dataset = gdal.Open(tif_path)
        if self.dataset is None:
            raise FileNotFoundError(f"Cannot open file: {tif_path}")

        self.transform_info = self.dataset.GetGeoTransform()
        if self.transform_info is None:
            raise ValueError("Failed to get geotransform from the dataset.")

        proj_info = self.dataset.GetProjection()
        if proj_info is None:
            raise ValueError("Failed to get projection from the dataset.")

        self.band = self.dataset.GetRasterBand(1)
        if self.band is None:
            raise ValueError("Failed to get raster band from the dataset.")

    def get_elevation(self, lon, lat):
        try:
            srcX = lon
            srcY = lat
            x_min = self.transform_info[0]
            x_max = x_min + self.transform_info[1] * self.dataset.RasterXSize
            y_max = self.transform_info[3]
            y_min = y_max + self.transform_info[5] * self.dataset.RasterYSize
            if not (x_min <= srcX <= x_max and y_min <= srcY <= y_max):
                raise ValueError(f"lon: {srcX} lat: {srcY}The given coordinates are outside the GeoTIFF boundaries.")
            px = int((srcX - self.transform_info[0]) / self.transform_info[1])
            py = int((srcY - self.transform_info[3]) / self.transform_info[5])
            return self.band.ReadAsArray(px, py, 1, 1)[0][0]
        except Exception as e:
            print(f"Coordinate transformation failed: {e}")
            return None


if __name__ == "__main__":
    # GeoTIFF 文件路径
    tif_path = "tif_file/noto.tif"
    # 经纬度坐标
    lon = 140.09253
    lat = 36.07797
    try:
        ele = elevation_utils(tif_path)
        value_ele = ele.get_elevation(lon, lat)
        if value_ele is not None:
            print(f"lon: {lon}, lat: {lat}, elevation: {value_ele} ")
        else:
            print(f"Cannot determine elevation for coordinates lon: {lon}, lat: {lat}")
    except Exception as e:
        print(f"Error: {e}")
