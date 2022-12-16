import asciichartpy
from kubePtop.global_attrs import GlobalAttrs

class AsciiGraph:
    """
    Create a Terminal Graph with 'asciichartpy'
    1. create a graph with 'create_graph()'
    2. update the graph with 'update_lst()'
    
    - the graph is write and upate to the '.graph' attribute (str)
    - the lines-names mapped colors are written to '.colors_description_str' attribute (str)

    # Example #
    import random
    import time

    devices = ["eth0", "eth1", "eth2", "eth3"]
    graph = Graph()
    graph.create_graph(devices, height=16, width=45)

    while True:
        graph.update_lst("eth0", random.randrange(1, 5))
        graph.update_lst("eth1", random.randrange(10, 15))
        graph.update_lst("eth2", random.randrange(20, 25))
        graph.update_lst("eth3", random.randrange(30, 35))
        time.sleep(1)

        print(graph.graph + f"\n {graph.colors_description_str}")
    exit(1)
    """
    def __init__(self):
        self.colors = [asciichartpy.lightgreen, asciichartpy.lightblue, asciichartpy.lightyellow, asciichartpy.lightred, asciichartpy.lightcyan, asciichartpy.lightgray, asciichartpy.lightmagenta, asciichartpy.red, asciichartpy.green, asciichartpy.blue, asciichartpy.yellow, asciichartpy.cyan, asciichartpy.darkgray] # asciichartpy.black, asciichartpy.white
        self.colors_lst_map = {}
        self.names = {}
        self.hight = 20
        self.width = 40
        self.colors_description_str = ""
        self.graph = ""
        self.series = []
        self.used_colors = []
        self.init_first_lst_done = False 

    def pick_color(self):
        """
        """
        # Pick a random color
        chosen_color = self.colors[0]
        # remove the color from the list (so it can't be choosen again.)
        self.colors.pop(0)
        return chosen_color

    def create_graph(self, names=[], height=17, width=45, format='{:8.0f} MB'):
        """
        INPUT: a dctionary where the key is the data line name and value is the list (each list represent data line.)
            Example: ["eth0", "eth1", "eth2"]
        RETURN: Text Graph
        """
        self.hight = height
        self.width = width
        self.names = names

        # if len(names) > len(self.colors):
        #     raise Exception(f"Input lists number ({len(names)}) are more than the supported lists number ({len(self.colors)})")

        # Handle if the number of items > available colors
        if len(names) > len(self.colors):
            index = len(self.colors)
            while len(self.colors) < len(names):
                self.colors.append(asciichartpy.colored(char=list(names)[index] + " ", color=asciichartpy.black))
                index +=1

        for name in names:
            color = self.pick_color()
            self.colors_lst_map[name] = {
                "lst": [],
                "color": color
            }
            self.used_colors.append(color)
    
        self.colors_description()

        self.config = {
        "colors": self.used_colors,
        "offset": 3,             # axis offset from the left (min 2)
        "padding": '       ',    # padding string for label formatting (can be overrided)
        "height":  self.hight,   ## any height you want
        "format": format
        }
        graph =  asciichartpy.plot(series=self.series, cfg=self.config)
        self.graph = graph
    
    def replace_lst(self, name, lst):
        if name not in self.names:
            raise Exception("List name not found")

        # Replace the list
        self.colors_lst_map[name]['lst'] = lst[-self.width:] # Keep the width

        # Update the series list
        self.series = []
        for name, info in self.colors_lst_map.items():
            self.series.append(info['lst'])
        
        # Update the graph with list update
        graph =  asciichartpy.plot(self.series, self.config)
        self.graph = graph
        return graph

    def update_lst(self, name, item):
        """
        """
        if name not in self.names:
            raise Exception("List name not found")
        # if (not isinstance(item, int)) or (not isinstance(item, float)):
            # raise Exception("List item should be int or float only")

        # Update the list
        self.colors_lst_map[name].get('lst').append(item)

        # Keep the width
        if len(self.colors_lst_map[name]['lst']) > self.width:
            self.colors_lst_map[name]['lst'].pop(0)
        
        # Update the series list
        for name, info in self.colors_lst_map.items():
            self.series.append(info['lst'])
        
        # Put a "0" at the begining to show the full hight of the chart
        if GlobalAttrs.start_graphs_with_zero:
            if not self.init_first_lst_done:
                if len(self.colors_lst_map) > 0:
                    self.init_first_lst_done = True
                    self.series[0].insert(0,0)
            ## Maybe can have a counter to remove the inserted '0' [if needed.]
            # else:
            #     self.series[0].pop(0)
        
        # Update the graph with list update
        graph =  asciichartpy.plot(self.series, self.config)
        self.graph = graph
        return graph

    def colors_description(self):
        """
        """
        str_ = ""
        for name, info in self.colors_lst_map.items():
            str_ = str_ + f"{info['color'] + name} "
        str_ = str_ + asciichartpy.reset
        self.colors_description_str = str_
