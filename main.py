import svgwrite
import svgwrite.shapes
import svgwrite.text
import svgwrite.container
import math
import yaml

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
    def __init__(self,width=1000,height=1000):
        self.cities = {}
        self.connections = []

    def add_city(self,city:City):
        self.cities[city.name] = city

    def add_connection(self,connection:Connection):
        self.connections.append(connection)

    @staticmethod
    def from_yaml(file_path):
        loaded_yaml = yaml.load(open(file_path,'r'))
        input_width = loaded_yaml['image_meta_info']['width_px']
        input_height = loaded_yaml['image_meta_info']['height_px']
        px_per_in = loaded_yaml['output_meta_info']['px_per_in']
        output_width = loaded_yaml['output_meta_info']['width_in'] * px_per_in
        output_height = loaded_yaml['output_meta_info']['height_in'] * px_per_in
        if input_width/input_height > output_width/output_height:
            scaling_factor = output_width/input_width
        else:
            scaling_factor = output_height/input_height
        ret = Map()


        for city_info in loaded_yaml['cities']:
            name = city_info['name']
            x = city_info['x'] * scaling_factor
            y = city_info['y'] * scaling_factor
            ret.add_city(City(name,x,y))

        for connection_info in loaded_yaml['connections']:
            start = connection_info['start']
            end = connection_info['end']
            length = connection_info['length']
            primary_color = connection_info['primary_color']
            secondary_color = connection_info['secondary_color']
            connection = Connection(start,end,length,primary_color,secondary_color)
            ret.add_connection(connection)

        return ret

class MapDrawer(object):
    train_width = 25.4
    train_height =  10
    train_spacing = 1.5
    font_height = 2

    @staticmethod
    def train_space_element(color,centered_position=(0,0),rotation=0):
        size = (MapDrawer.train_width,MapDrawer.train_height)
        transform = MapDrawer.rotate_center_string(centered_position,size,rotation)
        insert_location = MapDrawer.uncentered_position(centered_position,size)
        return svgwrite.shapes.Rect(insert=insert_location,size=size, fill=color,stroke='black',stroke_width='1', transform=transform)

    @staticmethod
    def city_marker_element(position:tuple):
        g = svgwrite.container.Group()
        g.add(svgwrite.shapes.Circle(position,r=3,fill='black'))
        return g

    @staticmethod
    def city_element(city:City):
        g = svgwrite.container.Group()
        g.add(MapDrawer.city_marker_element(city.position))
        g.add(svgwrite.text.Text(city.name,x=[city.position[0]],y=[city.position[1]],font_size='4'))
        return g

    @staticmethod
    def map_style_element():
        styles = svgwrite.container.Style(content='.small { font: italic 2px sans-serif; }')
        # styles.add()
        return styles

    @staticmethod
    def train_path_element(length,start_point,end_point,primary_color,secondary_color=None):
        group = svgwrite.container.Group()
        train_space_locations = []
        rotation = math.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])
        width = MapDrawer.train_width

        height = MapDrawer.train_height
        spacing = MapDrawer.train_spacing

        if secondary_color:
            center_offset = (height + spacing) / 2
            perpendicular_angle = rotation + math.pi / 2
            offset_vector = (math.cos(perpendicular_angle)*center_offset,math.sin(perpendicular_angle)*center_offset)

            left_start = (start_point[0]+offset_vector[0],start_point[1]+offset_vector[1])
            left_end = (end_point[0]+offset_vector[0],end_point[1]+offset_vector[1])
            left_path = MapDrawer.train_path_element(length,left_start,left_end,primary_color)

            right_start = (start_point[0]-offset_vector[0],start_point[1]-offset_vector[1])
            right_end = (end_point[0]-offset_vector[0],end_point[1]-offset_vector[1])
            right_path = MapDrawer.train_path_element(length,right_start,right_end,secondary_color)

            group.add(left_path)
            group.add(right_path)
        else:
            if length %2 == 1:
                center_point = (start_point[0]+(end_point[0]-start_point[0])/2,start_point[1]+(end_point[1]-start_point[1])/2)
                train_space_locations.append(center_point)
                bottom_location = center_point
                top_location = center_point
            else:
                center_point = (start_point[0]+(end_point[0]-start_point[0])/2,start_point[1]+(end_point[1]-start_point[1])/2)
                top_location = (center_point[0] + (width+spacing)/2*math.cos(rotation),center_point[1] + (width+spacing)/2*math.sin(rotation))
                bottom_location = (center_point[0] - (width+spacing)/2*math.cos(rotation),center_point[1] - (width+spacing)/2*math.sin(rotation))
                train_space_locations.append(top_location)
                train_space_locations.append(bottom_location)
            while len(train_space_locations) < length:
                bottom_location = (bottom_location[0] - (width+spacing) * math.cos(rotation), bottom_location[1] - (width+spacing)* math.sin(rotation))
                train_space_locations.append(bottom_location)
                top_location = (top_location[0] + (width+spacing) * math.cos(rotation), top_location[1] + (width+spacing) * math.sin(rotation))
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
        x,y = 30, 20

        drawn_map = svgwrite.Drawing(size=(x * units_per_inch,y * units_per_inch))

        for city in map.cities.values():
            drawn_map.add(MapDrawer.city_element(city))

        for connection in map.connections:
            city_1, city_2 = map.cities[connection.city_1_name], map.cities[connection.city_2_name]
            drawn_map.add(MapDrawer.train_path_element(connection.path_length,city_1.position,city_2.position,connection.path_1_color,connection.path_2_color))
        out_file_handle = open(out_file_name,mode='w')
        drawn_map.write(out_file_handle,pretty=True)

# m = Map()
# m.add_city(City('City A',10,10))
# m.add_city(City('City B',100,80))
# m.add_city(City('City C',100,10))
# m.add_connection(Connection('City A','City B',3,MapColors.GREY))
# m.add_connection(Connection('City C','City B',2,MapColors.PINK))

m = Map.from_yaml('iowa_cities.yaml')

MapDrawer.write_map('map.svg',m)