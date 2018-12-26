import svgwrite
import svgwrite.shapes
import svgwrite.text
import svgwrite.container
import math

class MapColors(object):
    GREY = 'grey'
    RED = 'red'
    BLUE = 'blue'
    PINK = 'pink'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    BLACK = 'black'
    WHITE = 'white'
    GREEN = 'green'



class City(object):
    def __init__(self,name:str,relative_x,relative_y):
        self.name = name
        self.position = (relative_x,relative_y)

class Connection(object):
    def __init__(self,city_1_name:str,city_2_name:str,path_length,path_1_color,path_2_color=None):
        self.city_1_name = city_1_name
        self.city_2_name = city_2_name
        self.path_length = path_length
        self.path_1_color = path_1_color
        self.path_2_color = path_2_color

    # Used for identifying if a path has been processed
    def getName(self):
        return self.city_1_name + self.city_2_name

class Map(object):
    def __init__(self):
        self.cities = {}
        self.connections = []

    def add_city(self,city:City):
        self.cities[city.name] = city

    def add_connection(self,connection:Connection):
        self.connections.append(connection)

class MapDrawer(object):
    @staticmethod
    def train_space_element(color,centered_position=(0,0),rotation=0):
        size = (25.4,10)
        return svgwrite.shapes.Rect(insert=MapDrawer.uncentered_position(centered_position,size),size=size, fill=color,stroke='black',stroke_width='1', transform=MapDrawer.rotate_center_string(centered_position,size,rotation))

    @staticmethod
    def city_marker_element(position:tuple):
        g = svgwrite.container.Group()
        g.add(svgwrite.shapes.Circle(position,r=3,fill='black'))
        return g

    @staticmethod
    def city_element(city:City):
        g = svgwrite.container.Group()
        g.add(MapDrawer.city_marker_element(city.position))
        g.add(svgwrite.text.Text(city.name,x=[city.position[0]],y=[city.position[1]]))
        return g

    @staticmethod
    def train_path_element(length,start_point,end_point,primary_color,secondary_color=None):
        group = svgwrite.container.Group()
        train_space_locations = []
        rotation = math.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])
        if length %2 == 1:
            # rotation = math.atan2(end_point[1]-start_point[1],end_point[0]-start_point[0])
            center_point = (start_point[0]+(end_point[0]-start_point[0])/2,start_point[1]+(end_point[1]-start_point[1])/2)
            train_space_locations.append(center_point)
            bottom_location = center_point
            top_location = center_point
        else:
            center_point = (start_point[0]+(end_point[0]-start_point[0])/2,start_point[1]+(end_point[1]-start_point[1])/2)
            top_location = (center_point[0] + 12.7*math.cos(rotation),center_point[1] + 12.7*math.sin(rotation))
            bottom_location = (center_point[0] - 12.7*math.cos(rotation),center_point[1] - 12.7*math.sin(rotation))
            train_space_locations.append(top_location)
            train_space_locations.append(bottom_location)
        while len(train_space_locations) < length:
            bottom_location = (bottom_location[0] - 25.4 * math.cos(rotation), bottom_location[1] - 25.4 * math.sin(rotation))
            train_space_locations.append(bottom_location)
            top_location = (top_location[0] + 25.4 * math.cos(rotation), top_location[1] + 25.4 * math.sin(rotation))
            train_space_locations.append(top_location)
        for location in train_space_locations:
            group.add(MapDrawer.train_space_element(primary_color,location,math.degrees(rotation)))
        return group

    @staticmethod
    def centered_position(position,size):
        return (position[0]+size[0]/2,position[1]+size[1]/2)

    @staticmethod
    def uncentered_position(centered_position,size):
        return (centered_position[0]-size[0]/2,centered_position[1]-size[1]/2)

    @staticmethod
    def rotate_center_string(centered_position,size,rotation):
        return 'rotate('+str(rotation)+', '+str(centered_position[0])+', '+str(centered_position[1])+')'

    @staticmethod
    def write_map(out_file_name:str,map:Map):
        units_per_inch = 25.4
        x,y = 10, 10
        drawn_map = svgwrite.Drawing(size=(x * units_per_inch,y * units_per_inch))
        # drawn_map.add(MapDrawer.train_space_element('red',centered_position=(20,30),rotation=90))
        for city in map.cities.values():
            drawn_map.add(MapDrawer.city_element(city))

        for connection in map.connections:
            city_1, city_2 = map.cities[connection.city_1_name], map.cities[connection.city_2_name]
            drawn_map.add(MapDrawer.train_path_element(connection.path_length,city_1.position,city_2.position,connection.path_1_color))

        # drawn_map.add(MapDrawer.train_path_element(4,(0,0),(100,300),'blue'))
        out_file_handle = open(out_file_name,mode='w')
        drawn_map.write(out_file_handle,pretty=True)

m = Map()
m.add_city(City('City A',10,10))
m.add_city(City('City B',100,80))
m.add_connection(Connection('City A','City B',3,MapColors.GREY))
MapDrawer.write_map('map.svg',m)