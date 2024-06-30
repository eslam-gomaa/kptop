import asciichartpy
from kubePtop.global_attrs import GlobalAttrs

class AsciiGraph:
    """
    Create a Terminal Graph with 'asciichartpy'
    1. create a graph with 'create_graph()'
    2. update the graph with 'update_lst()'

    - the graph is writen and upated to the '.graph' attribute (str)
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

        self.colors = [
            '\033[38;5;2m',    # Green
            '\033[38;5;1m',    # Maroon
            '\033[38;5;3m',    # Olive
            '\033[38;5;4m',    # Navy
            '\033[38;5;5m',    # Purple
            '\033[38;5;6m',    # Teal
            '\033[38;5;12m',   # Blue
            '\033[38;5;241m',  # Grey
            '\033[38;5;7m',    # Silver
            '\033[38;5;8m',    # Grey
            '\033[38;5;9m',    # Red
            '\033[38;5;10m',   # Lime
            '\033[38;5;11m',   # Yellow
            '\033[38;5;132m',  # HotPink3
            '\033[38;5;133m',  # MediumOrchid3
            '\033[38;5;134m',  # MediumOrchid
            '\033[38;5;135m',  # MediumPurple2
            '\033[38;5;136m',  # DarkGoldenrod
            '\033[38;5;137m',  # LightSalmon3
            '\033[38;5;138m',  # RosyBrown
            '\033[38;5;139m',  # Grey63
            '\033[38;5;140m',  # MediumPurple2
            '\033[38;5;141m',  # MediumPurple1
            '\033[38;5;13m',   # Fuchsia
            '\033[38;5;14m',   # Aqua
            # '\033[38;5;15m',   # White
            '\033[38;5;16m',   # Grey0
            '\033[38;5;17m',   # NavyBlue
            '\033[38;5;18m',   # DarkBlue
            '\033[38;5;19m',   # Blue3
            '\033[38;5;20m',   # Blue3
            '\033[38;5;21m',   # Blue1
            '\033[38;5;22m',   # DarkGreen
            '\033[38;5;23m',   # DeepSkyBlue4
            '\033[38;5;24m',   # DeepSkyBlue4
            '\033[38;5;25m',   # DeepSkyBlue4
            '\033[38;5;26m',   # DodgerBlue3
            '\033[38;5;27m',   # DodgerBlue2
            '\033[38;5;28m',   # Green4
            '\033[38;5;29m',   # SpringGreen4
            '\033[38;5;30m',   # Turquoise4
            '\033[38;5;31m',   # DeepSkyBlue3
            '\033[38;5;32m',   # DeepSkyBlue3
            '\033[38;5;33m',   # DodgerBlue1
            '\033[38;5;34m',   # Green3
            '\033[38;5;35m',   # SpringGreen3
            '\033[38;5;36m',   # DarkCyan
            '\033[38;5;37m',   # LightSeaGreen
            '\033[38;5;38m',   # DeepSkyBlue2
            '\033[38;5;39m',   # DeepSkyBlue1
            # '\033[38;5;0m',    # Black
            '\033[38;5;40m',   # Green3
            '\033[38;5;41m',   # SpringGreen3
            '\033[38;5;42m',   # SpringGreen2
            '\033[38;5;43m',   # Cyan3
            '\033[38;5;44m',   # DarkTurquoise
            '\033[38;5;45m',   # Turquoise2
            '\033[38;5;46m',   # Green1
            '\033[38;5;47m',   # SpringGreen2
            '\033[38;5;48m',   # SpringGreen1
            '\033[38;5;49m',   # MediumSpringGreen
            '\033[38;5;50m',   # Cyan2
            '\033[38;5;51m',   # Cyan1
            '\033[38;5;52m',   # DarkRed
            '\033[38;5;53m',   # DeepPink4
            '\033[38;5;54m',   # Purple4
            '\033[38;5;55m',   # Purple4
            '\033[38;5;56m',   # Purple3
            '\033[38;5;57m',   # BlueViolet
            '\033[38;5;58m',   # Orange4
            '\033[38;5;59m',   # Grey37
            '\033[38;5;60m',   # MediumPurple4
            '\033[38;5;61m',   # SlateBlue3
            '\033[38;5;62m',   # SlateBlue3
            '\033[38;5;63m',   # RoyalBlue1
            '\033[38;5;64m',   # Chartreuse4
            '\033[38;5;65m',   # DarkSeaGreen4
            '\033[38;5;66m',   # PaleTurquoise4
            '\033[38;5;67m',   # SteelBlue
            '\033[38;5;68m',   # SteelBlue3
            '\033[38;5;69m',   # CornflowerBlue
            '\033[38;5;70m',   # Chartreuse3
            '\033[38;5;71m',   # DarkSeaGreen4
            '\033[38;5;72m',   # CadetBlue
            '\033[38;5;73m',   # CadetBlue
            '\033[38;5;74m',   # SkyBlue3
            '\033[38;5;75m',   # SteelBlue1
            '\033[38;5;76m',   # Chartreuse3
            '\033[38;5;77m',   # PaleGreen3
            '\033[38;5;78m',   # SeaGreen3
            '\033[38;5;79m',   # Aquamarine3
            '\033[38;5;80m',   # MediumTurquoise
            '\033[38;5;81m',   # SteelBlue1
            '\033[38;5;82m',   # Chartreuse2
            '\033[38;5;83m',   # SeaGreen2
            '\033[38;5;84m',   # SeaGreen1
            '\033[38;5;85m',   # SeaGreen1
            '\033[38;5;86m',   # Aquamarine1
            '\033[38;5;87m',   # DarkSlateGray2
            '\033[38;5;88m',   # DarkRed
            '\033[38;5;89m',   # DeepPink4
            '\033[38;5;90m',   # DarkMagenta
            '\033[38;5;91m',   # DarkMagenta
            '\033[38;5;92m',   # DarkViolet
            '\033[38;5;93m',   # Purple
            '\033[38;5;94m',   # Orange4
            '\033[38;5;95m',   # LightPink4
            '\033[38;5;96m',   # Plum4
            '\033[38;5;97m',   # MediumPurple3
            '\033[38;5;98m',   # MediumPurple3
            '\033[38;5;99m',   # SlateBlue1
            '\033[38;5;100m',  # Yellow4
            '\033[38;5;101m',  # Wheat4
            '\033[38;5;102m',  # Grey53
            '\033[38;5;103m',  # LightSlateGrey
            '\033[38;5;104m',  # MediumPurple
            '\033[38;5;105m',  # LightSlateBlue
            '\033[38;5;106m',  # Yellow4
            '\033[38;5;107m',  # DarkOliveGreen3
            '\033[38;5;108m',  # DarkSeaGreen
            '\033[38;5;109m',  # LightSkyBlue3
            '\033[38;5;110m',  # LightSkyBlue3
            '\033[38;5;111m',  # SkyBlue2
            '\033[38;5;112m',  # Chartreuse2
            '\033[38;5;113m',  # DarkOliveGreen3
            '\033[38;5;114m',  # PaleGreen3
            '\033[38;5;115m',  # DarkSeaGreen3
            '\033[38;5;116m',  # DarkSlateGray3
            '\033[38;5;117m',  # SkyBlue1
            '\033[38;5;118m',  # Chartreuse1
            '\033[38;5;119m',  # LightGreen
            '\033[38;5;120m',  # LightGreen
            '\033[38;5;121m',  # PaleGreen1
            '\033[38;5;122m',  # Aquamarine1
            '\033[38;5;123m',  # DarkSlateGray1
            '\033[38;5;124m',  # Red3
            '\033[38;5;125m',  # DeepPink4
            '\033[38;5;126m',  # MediumVioletRed
            '\033[38;5;127m',  # Magenta3
            '\033[38;5;128m',  # DarkViolet
            '\033[38;5;129m',  # Purple
            '\033[38;5;130m',  # DarkOrange3
            '\033[38;5;131m',  # IndianRed
            '\033[38;5;142m',  # Gold3
            '\033[38;5;143m',  # DarkKhaki
            '\033[38;5;144m',  # NavajoWhite3
            '\033[38;5;145m',  # Grey69
            '\033[38;5;146m',  # LightSteelBlue3
            '\033[38;5;147m',  # LightSteelBlue
            '\033[38;5;148m',  # Yellow3
            '\033[38;5;149m',  # DarkOliveGreen3
            '\033[38;5;150m',  # DarkSeaGreen3
            '\033[38;5;151m',  # DarkSeaGreen2
            '\033[38;5;152m',  # LightCyan3
            '\033[38;5;153m',  # LightSkyBlue1
            '\033[38;5;154m',  # GreenYellow
            '\033[38;5;155m',  # DarkOliveGreen2
            '\033[38;5;156m',  # PaleGreen1
            '\033[38;5;157m',  # DarkSeaGreen2
            '\033[38;5;158m',  # DarkSeaGreen1
            '\033[38;5;159m',  # PaleTurquoise1
            '\033[38;5;160m',  # Red3
            '\033[38;5;161m',  # DeepPink3
            '\033[38;5;162m',  # DeepPink3
            '\033[38;5;163m',  # Magenta3
            '\033[38;5;164m',  # Magenta3
            '\033[38;5;165m',  # Magenta2
            '\033[38;5;166m',  # DarkOrange3
            '\033[38;5;167m',  # IndianRed
            '\033[38;5;168m',  # HotPink3
            '\033[38;5;169m',  # HotPink2
            '\033[38;5;170m',  # Orchid
            '\033[38;5;171m',  # MediumOrchid1
            '\033[38;5;172m',  # Orange3
            '\033[38;5;173m',  # LightSalmon3
            '\033[38;5;174m',  # LightPink3
            '\033[38;5;175m',  # Pink3
            '\033[38;5;176m',  # Plum3
            '\033[38;5;177m',  # Violet
            '\033[38;5;178m',  # Gold3
            '\033[38;5;179m',  # LightGoldenrod3
            '\033[38;5;180m',  # Tan
            '\033[38;5;181m',  # MistyRose3
            '\033[38;5;182m',  # Thistle3
            '\033[38;5;183m',  # Plum2
            '\033[38;5;184m',  # Yellow3
            '\033[38;5;185m',  # Khaki3
            '\033[38;5;186m',  # LightGoldenrod2
            '\033[38;5;187m',  # LightYellow3
            '\033[38;5;188m',  # Grey84
            '\033[38;5;189m',  # LightSteelBlue1
            '\033[38;5;190m',  # Yellow2
            '\033[38;5;191m',  # DarkOliveGreen1
            '\033[38;5;192m',  # DarkOliveGreen1
            '\033[38;5;193m',  # DarkSeaGreen1
            '\033[38;5;194m',  # Honeydew2
            '\033[38;5;195m',  # LightCyan1
            '\033[38;5;196m',  # Red1
            '\033[38;5;197m',  # DeepPink2
            '\033[38;5;198m',  # DeepPink1
            '\033[38;5;199m',  # DeepPink1
            '\033[38;5;200m',  # Magenta2
            '\033[38;5;201m',  # Magenta1
            '\033[38;5;202m',  # OrangeRed1
            '\033[38;5;203m',  # IndianRed1
            '\033[38;5;204m',  # IndianRed1
            '\033[38;5;205m',  # HotPink
            '\033[38;5;206m',  # HotPink
            '\033[38;5;207m',  # MediumOrchid1
            '\033[38;5;208m',  # DarkOrange
            '\033[38;5;209m',  # Salmon1
            '\033[38;5;210m',  # LightCoral
            '\033[38;5;211m',  # PaleVioletRed1
            '\033[38;5;212m',  # Orchid2
            '\033[38;5;213m',  # Orchid1
            '\033[38;5;214m',  # Orange1
            '\033[38;5;215m',  # SandyBrown
            '\033[38;5;216m',  # LightSalmon1
            '\033[38;5;217m',  # LightPink1
            '\033[38;5;218m',  # Pink1
            '\033[38;5;219m',  # Plum1
            '\033[38;5;220m',  # Gold1
            '\033[38;5;221m',  # LightGoldenrod2
            '\033[38;5;222m',  # LightGoldenrod2
            '\033[38;5;223m',  # NavajoWhite1
            '\033[38;5;224m',  # MistyRose1
            '\033[38;5;225m',  # Thistle1
            '\033[38;5;226m',  # Yellow1
            '\033[38;5;227m',  # LightGoldenrod1
            '\033[38;5;228m',  # Khaki1
            '\033[38;5;229m',  # Wheat1
            '\033[38;5;230m',  # Cornsilk1
            '\033[38;5;231m',  # Grey100
            '\033[38;5;232m',  # Grey3
            '\033[38;5;233m',  # Grey7
            '\033[38;5;234m',  # Grey11
            '\033[38;5;235m',  # Grey15
            '\033[38;5;236m',  # Grey19
            '\033[38;5;237m',  # Grey23
            '\033[38;5;238m',  # Grey27
            '\033[38;5;239m',  # Grey30
            '\033[38;5;240m',  # Grey35
        ]
        self.colors_lst_map = {}
        self.names = []
        self.height = 20
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

    def create_graph(self, names=[], height=17, width=45, max_height=20, max_width=50, format='{:8.0f} MB'):
        """
        INPUT: a dctionary where the key is the data line name and value is the list (each list represent data line.)
            Example: ["eth0", "eth1", "eth2"]
        RETURN: Text Graph
        """

        if height == 0:
            auto_height = max(10, len(names) * 2)
            self.height = max_height if auto_height > max_height else auto_height
        else:
            self.height = height

        if width == 0:
            auto_width = max(len(name) for name in names)
            self.width = max_width if auto_width > max_width else auto_width
        else:
            self.width = width

        self.names = names

        # if len(names) > len(self.colors):
        #     raise Exception(f"Input lists number ({len(names)}) are more than the supported lists number ({len(self.colors)})")

        # Handle if the number of items > available colors
        if len(names) > len(self.colors):
            index = len(self.colors)
            while len(self.colors) < len(names):
                # self.colors.append(asciichartpy.colored(char=list(names)[index] + " ", color=asciichartpy.black))
                self.colors.append(asciichartpy.black)
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
            "height":  self.height,   ## any height you want
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
            self.used_colors.append(info['color'])

        # Update the graph with list update
        graph =  asciichartpy.plot(self.series, self.config)
        self.graph = graph
        return graph

    def update_lst(self, name, item, format):
        """
        Update the list associated with a name and ensure used colors match the series.
        """
        if name not in self.names:
            color = self.pick_color()
            self.colors_lst_map[name] = {
                "lst": [],
                "color": color
            }
            self.names.append(name)

        self.colors_lst_map[name]['lst'].append(item)

        if len(self.colors_lst_map[name]['lst']) > self.width:
            self.colors_lst_map[name]['lst'].pop(0)

        # Update the series list and used colors
        self.series = [info['lst'] for name, info in self.colors_lst_map.items()]
        self.used_colors = [info['color'] for name, info in self.colors_lst_map.items()]

        if GlobalAttrs.start_graphs_with_zero:
            if not self.init_first_lst_done:
                if len(self.colors_lst_map) > 0:
                    self.init_first_lst_done = True
                    self.series[0].insert(0, 0)

        self.config = {
            "colors": self.used_colors,
            "offset": 3,
            "padding": '       ',
            "height": self.height,
            "format": format
        }

        graph = asciichartpy.plot(self.series, self.config)
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
