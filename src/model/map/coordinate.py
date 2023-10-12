import haversine as hs

class Coordinate():  
    
    """
    [Class] Coordinate
    A class to represent a coordinate. Also used as a vector representation.
    
    Properties:
        - lat : latitude.
        - lon : longitude.
    """
    
    def __init__(self, lat: float, lon: float):
        """
        [Constructor]
        Initialize an empty node.

        Parameter:
            - lat : [Double]latitude.
            - lon : [Double]longitude.
        """
        self.lat = lat
        self.lon = lon

    def get_lat_lon_in_figures(self):
        return (float(format(self.lat, '.5f')), float(format(self.lon, '.5f')))

    def get_lat(self):
        return float(format(self.lat, '.5f'))

    def get_lon(self):
        return float(format(self.lon, '.5f'))

    def get_lat_lon(self):
        """
        [Method] get_lat_lon
        return a tuple of lat and lon in that order. (usefull for printing strings)
        
        Return:[(Double,Double)](lat,lon)
        """
        return (self.lat,self.lon)
    
    def get_lon_lat(self):
        """
        [Method] get_lat_lon
        return a tuple of lat and lon in that order. (usefull for printing strings)
        
        Return:[(Double,Double)](lon,lat)
        """
        return (self.lon,self.lat)

    def translate(self,lat =0,lon = 0):
        """
        [Method] translate
        translate/move this coordinate

        Parameter:
            - lat : [Double] latitude translation.
            - lon : [Double] longitude translation.
        """
        self.lat += lat
        self.lon += lon
    
    def __str__(self):
        """
        [Method] __str__
        Generate the Coordinate info string and return it.
        
        Return: [string] String of summarized map Information.
        """
        tempstring = f"[Coordinate]\n\t(lat = {self.lat}, lon = {self.lon})"
        return tempstring

    def clone(self):
        return Coordinate(self.lat,self.lon)
    
    def new_coordinate_with_translation(self,lat =0,lon = 0):
        """
        [Method] new_coordinate_with_translation
        create a new coordinate and apply a translation from this coordinate

        Parameter:
            - lat : [Double] latitude translation.
            - lon : [Double] longitude translation.
            
        return :
            - [Coordinate] a clone of this coordinate with the translation applied.
        """
        temp = Coordinate(self.lat+lat,self.lon+lon)
        return temp
    
    def new_coordinate_with_scale(self,scale):
        """
        [Method] new_coordinate_with_scale
        create a new coordinate which is the scale of this vector

        Parameter:
            - scale : [Double] scaling factor.
            
        return :
            - [Coordinate] a clone of this coordinate with the scaling applied.

        """
        temp = Coordinate(self.lat*scale,self.lon*scale)
        return temp
       
    def calculate_distance(self,lat, lon):
        """
        [Method] calculate_distance
        calculate_distance to other coordinate
        
        Parameter:
            - targetCoordinate : [Coordinate] target Coordinate.
            
        Return: [Double] Distance in Meter
        """
        return hs.haversine(self.get_lat_lon(), (lat, lon), unit=hs.Unit.METERS)
    
    def get_vector_distance(self,targetCoordinate):
        """
        [Method] get_vector_distance
        Get distance in vector format. (Will be returned in coordinate object for ease of use)
        
        Parameter:
            - targetCoordinate : [Coordinate] target Coordinate.
        
        Return: [Coordinate] distance in vector format
        """
        return Coordinate(self.lat - targetCoordinate.lat, self.lon - targetCoordinate.lon)
    