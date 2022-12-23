import time
from tabulate import tabulate
# import textwrap
from datetime import datetime, timezone
import threading
import rich
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import SpinnerColumn, Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.console import Console, Group
from rich.rule import Rule
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
import traceback


from kubePtop.global_attrs import GlobalAttrs
from kubePtop.node_metrics import PrometheusNodeMetrics
from kubePtop.ascii_graph import AsciiGraph
from kubePtop.helper import Helper
helper_ = Helper()

from kubePtop.logging import Logging

class Node_Monitoring(PrometheusNodeMetrics):
    def __init__(self):
        super().__init__()
        self.dashboards = ['default', 'pvc']


    
    def list_dashboards(self):
        # Print it with tabulate table.
        print(self.dashboards)
        
    def display_dashboard(self, dashboard, node_name):
        if dashboard not in self.dashboards:
            print(f"ERROR -- Dashboard '{dashboard}' not found")
            Logging.log.error(f"ERROR -- Dashboard '{dashboard}' not found")
            print("Available dashboards:")
            print(self.list_dashboards())

        if dashboard == 'default':
            self.node_monitor_dashboard_default(node_name)
        if dashboard == 'pvc':
            self.node_monitor_dashboard_pvc(node_name)



    def node_monitor_dashboard_default(self, node_name):
        # Print loading because the layout may take few seconds to start (Probably due to slow connection)
        rich.print("[blink]Loading ...", end="\r")

        def make_layout() -> Layout:
            """
            The layout structure
            """
            layout = Layout(name="root")

            layout.split(
                Layout(name="header", size=3),
                # Layout(name="header2", size=7, ratio=1),
                Layout(name="main", ratio=1),
                # Layout(name="footer", size=6, ratio=1)
            )
            layout["main"].split_row(
                # Layout(name="side",),
                Layout(name="body", ratio=3, minimum_size=100,),
            )
            # layout["side"].split(Layout(name="box1")) # , Layout(name="box2")
            # layout["body"].split(Layout(name="head", size=5, ratio=2), Layout(name="body1")) # , Layout(name="box2")
            layout["body"].split_row(Layout(name="body1", size=45), Layout(name="body2"),) # , Layout(name="box2")
            layout['body1'].split_column(Layout(name="body1_a"), Layout(name="body1_b", size=11))
            layout["body2"].split(Layout(name="body2_a", ratio=1), Layout(name="body2_b", ratio=1)) # , Layout(name="box2")
            layout['body2_b'].split_row(Layout(name="body2_b_a", ratio=1), Layout(name="body2_b_b", ratio=1))

            return layout

        class Header():
            """
            Display header with clock.
            """
            def __rich__(self) -> Panel:
                grid = Table.grid(expand=True)
                grid.add_column(justify="center", ratio=1)
                grid.add_column(justify="right")
                grid.add_row(
                    f"[b]Node: [/b] {node_name} ",
                    datetime.now().ctime().replace(":", "[blink]:[/]"),
                )
                return Panel(grid, style="green")

        class Node_Resources_Progress(PrometheusNodeMetrics):
            def __init__(self):
                super().__init__()
                self.progress_start()

            def progress_start(self):
                # node_metrics_json = self.nodeMetrics(node=node_name)
                # node_mem_metrics_json = node_metrics_json.get('memory')
                # node_cpu_metrics_json = node_metrics_json.get('cpu')
                # node_fs_metrics_json = node_metrics_json.get('fs')
                

                self.progress_threads_status = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=20),
                    # TextColumn("[progress.percentage]{task.percentage:>3.0f}"),
                    TextColumn("{task.fields[status]}"),
                )
                self.task_thread_refresh = self.progress_threads_status.add_task(description=f"[white]Interval Refresh", status=f"unknown")
                self.task_prometheus_server_connection = self.progress_threads_status.add_task(description=f"[white]Prometheus", status=f"unknown")

                self.progress_mem_total = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=20),
                    # TextColumn("[progress.percentage]{task.percentage:>3.0f}"),
                    TextColumn("{task.fields[status]}"),
                )
                # if node_mem_metrics_json.get('MemTotalBytes').get('success'):
                self.task_mem_total = self.progress_mem_total.add_task(description=f"[white]Mem Total    ", status="Loading")

                self.progress_mem = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )

                # if (node_mem_metrics_json.get('MemTotalBytes').get('success') and node_mem_metrics_json.get('MemAvailableBytes').get('success')):
                self.task_mem_used = self.progress_mem.add_task(completed=0, description=f"[white]Mem used", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemAvailableBytes').get('success'):
                # self.task_mem_available = self.progress_mem.add_task(completed=0, description=f"[white]Mem available", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemFreeBytes').get('success'):
                self.task_mem_free = self.progress_mem.add_task(completed=0, description=f"[white]Mem free", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemCachedBytes').get('success'):
                self.task_mem_cached = self.progress_mem.add_task(completed=0, description=f"[white]Mem cached   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemBuffersBytes').get('success'):
                self.task_mem_buffer = self.progress_mem.add_task(completed=0, description=f"[white]Mem buffer   ", total=100, status="Loading")

                self.progress_swap = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_mem_metrics_json.get('MemSwapTotalBytes').get('success'):
                self.task_swap_total = self.progress_swap.add_task(completed=0, description=f"[white]Swap Total   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemSwapTotalBytes').get('success'):
                self.task_swap_free = self.progress_swap.add_task(completed=0, description=f"[white]Swap free   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemSwapCachedBytes').get('success'):
                self.task_swap_cached = self.progress_swap.add_task(completed=0, description=f"[white]Swap cached   ", total=100, status="Loading")

                self.progress_cpu_used_avg = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_cpu_metrics_json.get('cpuUsageAVG').get('success'):
                self.task_cpu_used_avg = self.progress_cpu_used_avg.add_task(description="CPU used AVG[10m]", completed=0, total=100, status="Loading")
                
                self.progress_cpu = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        # TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_cpu_metrics_json.get('cpuLoadAvg1m').get('success'):
                self.task_cpu_load1avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 1m   ", status="Loading")                                        
                self.task_cpu_load5avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 5m   ", status="Loading")                                        
                self.task_cpu_load15avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 15m   ", status="Loading")                                        


                self.progress_fs_total = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        # TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_fs_metrics_json.get('nodeFsSize').get('success'):
                self.task_fs_size_total = self.progress_fs_total.add_task(description=f"[white]FS Total        ", status="Loading")        

                self.progress_fs = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_fs_metrics_json.get('nodeFsUsed').get('success'):
                self.task_fs_used = self.progress_fs.add_task(completed=0, description=f"[white]FS used   ", total=100, status="Loading")

                # if node_fs_metrics_json.get('nodeFsAvailable').get('success'):
                self.task_fs_available = self.progress_fs.add_task(completed=0, description=f"[white]FS available   ", total=100, status="Loading")



                self.group_memory = Group (
                    self.progress_mem_total,
                    self.progress_mem,
                    Rule(style='#AAAAAA'),
                    self.progress_swap,
                )

                self.group_cpu = Group (
                    self.progress_cpu_used_avg,
                    self.progress_cpu
                )

                self.group_fs = Group (
                    self.progress_fs_total,
                    self.progress_fs
                )

            def update(self):
                time.sleep(3)
                while True:
                    Logging.log.info("Getting node metrics to update the dashboard")
                    node_metrics_json = self.nodeMetrics(node=node_name)
                    Logging.log.debug("Node metrics Json:")
                    Logging.log.debug(node_metrics_json)
                    node_mem_metrics_json = node_metrics_json.get('memory')
                    node_cpu_metrics_json = node_metrics_json.get('cpu')
                    node_fs_metrics_json = node_metrics_json.get('fs')
            
                    self.progress_mem_total.update(self.task_mem_total, description=f"[white]Mem Total    ", status=f"     {helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemTotalBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_used, completed=node_mem_metrics_json.get('MemTotalBytes').get('result') - (node_mem_metrics_json.get('MemFreeBytes').get('result') + node_mem_metrics_json.get('MemBuffersBytes').get('result') + node_mem_metrics_json.get('MemCachedBytes').get('result')), description=f"[white]Mem used", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemTotalBytes').get('result') - (node_mem_metrics_json.get('MemFreeBytes').get('result') + node_mem_metrics_json.get('MemBuffersBytes').get('result') + node_mem_metrics_json.get('MemCachedBytes').get('result')))}")
                    # self.progress_mem.update(self.task_mem_available, completed=node_mem_metrics_json.get('MemAvailableBytes').get('result'), description=f"[white]Mem available", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemAvailableBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_free, completed=node_mem_metrics_json.get('MemFreeBytes').get('result'), description=f"[white]Mem free", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemFreeBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_cached, completed=node_mem_metrics_json.get('MemCachedBytes').get('result'), description=f"[white]Mem cached   ", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemCachedBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_buffer, completed=node_mem_metrics_json.get('MemBuffersBytes').get('result'), description=f"[white]Mem buffer   ", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemBuffersBytes').get('result'))}")

                    self.progress_swap.update(self.task_swap_total, completed=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), description=f"[white]Swap Total   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapTotalBytes').get('result'))}")
                    self.progress_swap.update(self.task_swap_free, completed=node_mem_metrics_json.get('MemSwapFreeBytes').get('result'), description=f"[white]Swap free   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapFreeBytes').get('result'))}")
                    self.progress_swap.update(self.task_swap_cached, completed=node_mem_metrics_json.get('MemSwapCachedBytes').get('result'), description=f"[white]Swap cached   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapCachedBytes').get('result'))}")

                    self.progress_cpu_used_avg.update(self.task_cpu_used_avg, completed=(node_cpu_metrics_json.get('cpuUsageAVG').get('result') / 2), description=f"[white]CPU used AVG[10m]  ", total=100, status="")
                    self.progress_cpu.update(self.task_cpu_load1avg, description=f"[white]CPU load avg 1m   ", status=node_cpu_metrics_json.get('cpuLoadAvg1m').get('result'))
                    self.progress_cpu.update(self.task_cpu_load5avg, description=f"[white]CPU load avg 5m   ", status=node_cpu_metrics_json.get('cpuLoadAvg5m').get('result'))
                    self.progress_cpu.update(self.task_cpu_load15avg, description=f"[white]CPU load avg 15m   ", status=node_cpu_metrics_json.get('cpuLoadAvg15m').get('result'))

                    self.progress_fs_total.update(self.task_fs_size_total, description=f"[white]FS Total        ", status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsSize').get('result')))
                    self.progress_fs.update(self.task_fs_used, completed=node_fs_metrics_json.get('nodeFsUsed').get('result'), description=f"[white]FS used   ", total=node_fs_metrics_json.get('nodeFsSize').get('result'), status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsUsed').get('result')))
                    self.progress_fs.update(self.task_fs_available, completed=node_fs_metrics_json.get('nodeFsAvailable').get('result'), description=f"[white]FS available   ", total=node_fs_metrics_json.get('nodeFsSize').get('result'), status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsAvailable').get('result')))
                    
                    if GlobalAttrs.debug:
                        Logging.log.debug(f"Waiting for interval '{GlobalAttrs.live_update_interval}' before the next update")
                    time.sleep(GlobalAttrs.live_update_interval)

            def check_thread_node_resources(self, restart=True):
                while True:
                    def thread_status():
                        status = ""
                        if self.thread_node_resources.is_alive():
                            status = f"alive [green]✔️"
                        else:
                            status = "dead [red]❌"
                            if restart:
                                # Restart thread
                                self.start_threads()
                        return status

                    self.progress_threads_status.update(task_id=self.task_thread_refresh, status=thread_status())                            
                    time.sleep(5)
            
            class ValidatePrometheuesConnection(PrometheusNodeMetrics):
                def __init__(self):
                    super().__init__()
                    self.result = {}

                def run(self):
                    while True:
                        time.sleep(5)
                        self.result = self.verify_prometheus_connection()
                        if GlobalAttrs.debug:
                            print("DEBUG -- Function: ValidatePrometheuesConnection")
                        Logging.log.info("Function: ValidatePrometheuesConnection")
                        Logging.log.info("Function: ValidatePrometheuesConnection, waiting for internal '5s' ")

            def check_thread_prometheus_server_connection(self):
                while True:

                    def thread_status():
                        result = self.vlaidate_prometheus_server.result
                        # if self.thread_check_thread_prometheus_server_connection.is_alive():
                        if result.get('connected') is None:
                            status = f"waiting [green]✔️"
                        elif result.get('connected'):
                            status = f"connected [green]✔️"
                        else:
                            status = f"{result.get('reason')} [red]❌"

                        return status
                    
                    self.progress_threads_status.update(task_id=self.task_prometheus_server_connection, status=f"{thread_status()} ({self.vlaidate_prometheus_server.result.get('status_code')})")
                    time.sleep(5)

            def start_threads(self):
                self.thread_node_resources = threading.Thread(target=self.update)
                self.thread_node_resources.daemon = True
                self.thread_node_resources.start()
                Logging.log.debug("Started Thread: thread_node_resources")
                
                self.vlaidate_prometheus_server = self.ValidatePrometheuesConnection()
                self.thread_prometheus_server_connection = threading.Thread(target=self.vlaidate_prometheus_server.run)
                self.thread_prometheus_server_connection.daemon = True
                self.thread_prometheus_server_connection.start()
                Logging.log.debug("Started Thread: thread_prometheus_server_connection")

            def watch_threads(self):
                self.thread_check_thread_node_resources = threading.Thread(target=self.check_thread_node_resources)
                self.thread_check_thread_node_resources.daemon = True
                self.thread_check_thread_node_resources.start()

                self.thread_check_thread_prometheus_server_connection = threading.Thread(target=self.check_thread_prometheus_server_connection)
                self.thread_check_thread_prometheus_server_connection.daemon = True
                self.thread_check_thread_prometheus_server_connection.start()


        try:
            node_metrics = PrometheusNodeMetrics()
            node_resources_progress = Node_Resources_Progress()

            progress_table = Table.grid(expand=True)
            progress_table.add_row(
                Panel(node_resources_progress.group_cpu, title="[b]CPU", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.group_memory, title="[b]Memory", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.group_fs, title='[b]FS "/"', padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.progress_threads_status, title="[b]Threads Status",padding=(1, 2), subtitle=""),
            )


            layout = make_layout()
            layout["header"].update(Header())
            layout["body1_a"].update(progress_table)
            layout['body1_b'].update(Panel("Made with [red]❤️[/red]", title='[b]Unused Space', padding=(1, 2),))


            layout["body2_a"].update(Panel("Loading ...", title="[b]Top Pods in Memory Usage", padding=(1, 1)))
            
            node_resources_progress.start_threads()
            node_resources_progress.watch_threads()

            update_disk_read_bytes_graph = True
            disk_read_bytes_graph = AsciiGraph()
            disk_read_bytes = self.nodeDiskReadBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'disk_read_bytes' metrics; Result:\n{disk_read_bytes}")
            else:
                Logging.log.info("Getting Pod 'disk_read_bytes' metrics")   
            if disk_read_bytes.get('success'):
                disk_read_bytes_graph.create_graph(disk_read_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                disk_read_bytes_graph.graph = disk_read_bytes.get('fail_reason')
                update_disk_read_bytes_graph = False

            update_network_received_bytes_graph = True
            network_received_bytes_graph =  AsciiGraph()
            network_received_bytes = self.nodeNetworkReceiveBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'network_received_bytes' metrics; Result:\n{network_received_bytes}")
            else:
                Logging.log.info("Getting Pod 'network_received_bytes' metrics")   
            if network_received_bytes.get('success'):
                network_received_bytes_graph.create_graph(network_received_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                network_received_bytes_graph.graph = network_received_bytes.get('fail_reason')
                update_network_received_bytes_graph = False

            update_network_transmit_bytes_graph = True
            network_transmit_bytes_graph =  AsciiGraph()
            network_transmit_bytes = self.nodeNetworkTransmitBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'network_transmit_bytes' metrics; Result:\n{network_transmit_bytes}")
            else:
                Logging.log.info("Getting Pod 'network_transmit_bytes' metrics")   
            if network_transmit_bytes.get('success'):
                network_transmit_bytes_graph.create_graph(network_transmit_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                network_transmit_bytes_graph.graph = network_transmit_bytes.get('fail_reason')
                update_network_transmit_bytes_graph = False



            update_disk_written_bytes_graph = True
            disk_written_bytes_graph = AsciiGraph()
            disk_written_bytes = self.nodeDiskWrittenBytes(node_name)
            if disk_written_bytes.get('success'):
                disk_written_bytes_graph.create_graph(disk_written_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                disk_written_bytes_graph.graph = disk_written_bytes.get('fail_reason')
                update_disk_written_bytes_graph = False

            layout["body2_b_b"].update(Panel(Markdown("Loading ..."), title="[b]Network IO", padding=(1, 1)))
            layout["body2_b_a"].update(Panel(Markdown("Loading ..."), title="[b]Disk IO", padding=(1, 1)))

            group_network_io = Group(
                Markdown("Bytes Received", justify='center'),
                Text.from_ansi(network_received_bytes_graph.graph + f"\n {network_received_bytes_graph.colors_description_str}"),
                Rule(style='#AAAAAA'),
                Markdown("Bytes Transmitted", justify='center'),
                Text.from_ansi(network_transmit_bytes_graph.graph + f"\n {network_transmit_bytes_graph.colors_description_str}")
            )

            group_disk_io = Group(
                Markdown("Bytes Read", justify='center'),
                Text.from_ansi(disk_read_bytes_graph.graph + f"\n {disk_read_bytes_graph.colors_description_str}"),
                Rule(style='#AAAAAA'),
                Markdown("Bytes Written", justify='center'),
                Text.from_ansi(disk_written_bytes_graph.graph + f"\n {disk_written_bytes_graph.colors_description_str}")
            )

            Logging.log.info("Starting the Layout.")
            with Live(layout, auto_refresh=True, screen=True, refresh_per_second=GlobalAttrs.live_update_interval):
                while True:
                    pod_memory_usage = node_metrics.PodMemTopUsage(node=node_name)
                    layout["body2_a"].update(Panel(pod_memory_usage, title="[b]Top Pods in Memory Usage", padding=(1, 1)))                    
                    Logging.log.info("Updating the Layout with 'Top Pods in Memory Usage'")
                    Logging.log.debug(f"Result:\n{pod_memory_usage}")
                    
                    if update_network_received_bytes_graph:
                        network_received_bytes = self.nodeNetworkReceiveBytes(node_name)
                        Logging.log.info("Updating Node 'network_received_bytes' metrics")
                        Logging.log.debug(network_received_bytes)
                        for device, value in network_received_bytes.get('result').items():
                            network_received_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    if update_network_transmit_bytes_graph:
                        Logging.log.info("Updating Node 'network_transmit_bytes' metrics")
                        Logging.log.debug(network_transmit_bytes)
                        network_transmit_bytes = self.nodeNetworkTransmitBytes(node_name)
                        for device, value in network_transmit_bytes.get('result').items():
                            network_transmit_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))
                    
                    if update_disk_read_bytes_graph:
                        disk_read_bytes = self.nodeDiskReadBytes(node_name)
                        Logging.log.info("Updating Node 'disk_read_bytes' metrics")
                        Logging.log.debug(disk_read_bytes)
                        for device, value in disk_read_bytes.get('result').items():
                            disk_read_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    if update_disk_written_bytes_graph:
                        disk_written_bytes = self.nodeDiskWrittenBytes(node_name)
                        Logging.log.info("Updating Node 'disk_written_bytes' metrics")
                        Logging.log.debug(disk_written_bytes)
                        for device, value in disk_written_bytes.get('result').items():
                            disk_written_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    if update_network_received_bytes_graph or update_network_transmit_bytes_graph:
                        group_network_io = Group(
                            Markdown("Bytes Received", justify='center'),
                            Text.from_ansi(network_received_bytes_graph.graph + f"\n {network_received_bytes_graph.colors_description_str}"),
                            Rule(style='#AAAAAA'),
                            Markdown("Bytes Transmitted", justify='center'),
                            Text.from_ansi(network_transmit_bytes_graph.graph + f"\n {network_transmit_bytes_graph.colors_description_str}")
                        )

                    if update_disk_read_bytes_graph or update_disk_written_bytes_graph:
                        group_disk_io = Group(
                            Markdown("Bytes Read", justify='center'),
                            Text.from_ansi(disk_read_bytes_graph.graph + f"\n {disk_read_bytes_graph.colors_description_str}"),
                            Rule(style='#AAAAAA'),
                            Markdown("Bytes Written", justify='center'),
                            Text.from_ansi(disk_written_bytes_graph.graph + f"\n {disk_written_bytes_graph.colors_description_str}")
                        )

                    layout["body2_b_b"].update(Panel(group_network_io, title="[b]Network IO", padding=(1, 1)))
                    layout["body2_b_a"].update(Panel(group_disk_io, title="[b]Disk IO", padding=(1, 1)))

                    Logging.log.info(f"waiting for the update interval '{GlobalAttrs.live_update_interval}' before updating the Layout ")
                    time.sleep(GlobalAttrs.live_update_interval)   
                    Logging.log.info(f"Updating the layout")

        except Exception as e:
            rich.print("\n[yellow]ERROR -- " + str(e))
            rich.print("\n[underline bold]Exception:")
            traceback.print_exc()
            exit(1)
        except KeyboardInterrupt:
            print("                 ", end="\r")
            rich.print("Ok")
            exit(0)


    def node_monitor_dashboard_pvc(self, node_name):
        # Print loading because the layout may take few seconds to start (Probably due to slow connection)
        rich.print("[blink]Loading ...", end="\r")

        def make_layout() -> Layout:
            """
            The layout structure
            """
            layout = Layout(name="root")

            layout.split(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
            )
            layout["main"].split_row(
                Layout(name="body", ratio=3, minimum_size=100,),
            )

            layout["body"].split_column(Layout(name="body1", size=23), Layout(name="body2"),) # , Layout(name="box2")
            return layout

        class Header():
            """
            Display header with clock.
            """
            def __rich__(self) -> Panel:
                grid = Table.grid(expand=True)
                grid.add_column(justify="center", ratio=1)
                grid.add_column(justify="right")
                grid.add_row(
                    f"[b]Node: [/b] {node_name} ",
                    datetime.now().ctime().replace(":", "[blink]:[/]"),
                )
                return Panel(grid, style="green")

        class Node_Resources_Progress(PrometheusNodeMetrics):
            def __init__(self):
                super().__init__()
                self.progress_start()

            def progress_start(self):
                # node_metrics_json = self.nodeMetrics(node=node_name)
                # node_mem_metrics_json = node_metrics_json.get('memory')
                # node_cpu_metrics_json = node_metrics_json.get('cpu')
                # node_fs_metrics_json = node_metrics_json.get('fs')
                

                self.progress_threads_status = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=20),
                    # TextColumn("[progress.percentage]{task.percentage:>3.0f}"),
                    TextColumn("{task.fields[status]}"),
                )
                self.task_thread_refresh = self.progress_threads_status.add_task(description=f"[white]Metrics Refresh", status=f"unknown")
                self.task_prometheus_server_connection = self.progress_threads_status.add_task(description=f"[white]Prometheus", status=f"unknown")

                self.progress_mem_total = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=20),
                    # TextColumn("[progress.percentage]{task.percentage:>3.0f}"),
                    TextColumn("{task.fields[status]}"),
                )
                # if node_mem_metrics_json.get('MemTotalBytes').get('success'):
                self.task_mem_total = self.progress_mem_total.add_task(description=f"[white]Mem Total    ", status="Loading")

                self.progress_mem = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )

                # if (node_mem_metrics_json.get('MemTotalBytes').get('success') and node_mem_metrics_json.get('MemAvailableBytes').get('success')):
                self.task_mem_used = self.progress_mem.add_task(completed=0, description=f"[white]Mem used", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemAvailableBytes').get('success'):
                # self.task_mem_available = self.progress_mem.add_task(completed=0, description=f"[white]Mem available", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemFreeBytes').get('success'):
                self.task_mem_free = self.progress_mem.add_task(completed=0, description=f"[white]Mem free", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemCachedBytes').get('success'):
                self.task_mem_cached = self.progress_mem.add_task(completed=0, description=f"[white]Mem cached   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemBuffersBytes').get('success'):
                self.task_mem_buffer = self.progress_mem.add_task(completed=0, description=f"[white]Mem buffer   ", total=100, status="Loading")

                self.progress_swap = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_mem_metrics_json.get('MemSwapTotalBytes').get('success'):
                self.task_swap_total = self.progress_swap.add_task(completed=0, description=f"[white]Swap Total   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemSwapTotalBytes').get('success'):
                self.task_swap_free = self.progress_swap.add_task(completed=0, description=f"[white]Swap free   ", total=100, status="Loading")
                # if node_mem_metrics_json.get('MemSwapCachedBytes').get('success'):
                self.task_swap_cached = self.progress_swap.add_task(completed=0, description=f"[white]Swap cached   ", total=100, status="Loading")

                self.progress_cpu_used_avg = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_cpu_metrics_json.get('cpuUsageAVG').get('success'):
                self.task_cpu_used_avg = self.progress_cpu_used_avg.add_task(description="CPU used AVG[10m]", completed=0, total=100, status="Loading")
                
                self.progress_cpu = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        # TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_cpu_metrics_json.get('cpuLoadAvg1m').get('success'):
                self.task_cpu_load1avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 1m   ", status="Loading")                                        
                self.task_cpu_load5avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 5m   ", status="Loading")                                        
                self.task_cpu_load15avg = self.progress_cpu.add_task(description=f"[white]CPU load avg 15m   ", status="Loading")                                        


                self.progress_fs_total = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        # TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_fs_metrics_json.get('nodeFsSize').get('success'):
                self.task_fs_size_total = self.progress_fs_total.add_task(description=f"[white]FS Total        ", status="Loading")        

                self.progress_fs = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                # if node_fs_metrics_json.get('nodeFsUsed').get('success'):
                self.task_fs_used = self.progress_fs.add_task(completed=0, description=f"[white]FS used   ", total=100, status="Loading")

                # if node_fs_metrics_json.get('nodeFsAvailable').get('success'):
                self.task_fs_available = self.progress_fs.add_task(completed=0, description=f"[white]FS available   ", total=100, status="Loading")



                self.group_memory = Group (
                    self.progress_mem_total,
                    self.progress_mem,
                    Rule(style='#AAAAAA'),
                    self.progress_swap,
                )

                self.group_cpu = Group (
                    self.progress_cpu_used_avg,
                    self.progress_cpu
                )

                self.group_fs = Group (
                    self.progress_fs_total,
                    self.progress_fs
                )

            def update(self):
                time.sleep(3)
                while True:
                    Logging.log.info("Getting node metrics to update the dashboard")
                    node_metrics_json = self.nodeMetrics(node=node_name)
                    if GlobalAttrs.debug:
                        Logging.log.info("Node metrics Json:")
                        Logging.log.debug(node_metrics_json)
                    node_mem_metrics_json = node_metrics_json.get('memory')
                    node_cpu_metrics_json = node_metrics_json.get('cpu')
                    node_fs_metrics_json = node_metrics_json.get('fs')
            
                    self.progress_mem_total.update(self.task_mem_total, description=f"[white]Mem Total    ", status=f"     {helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemTotalBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_used, completed=node_mem_metrics_json.get('MemTotalBytes').get('result') - (node_mem_metrics_json.get('MemFreeBytes').get('result')), description=f"[white]Mem used", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemTotalBytes').get('result') - (node_mem_metrics_json.get('MemFreeBytes').get('result') + node_mem_metrics_json.get('MemBuffersBytes').get('result') + node_mem_metrics_json.get('MemCachedBytes').get('result')))}")
                    # self.progress_mem.update(self.task_mem_available, completed=node_mem_metrics_json.get('MemAvailableBytes').get('result'), description=f"[white]Mem available", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemAvailableBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_free, completed=node_mem_metrics_json.get('MemFreeBytes').get('result'), description=f"[white]Mem free", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemFreeBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_cached, completed=node_mem_metrics_json.get('MemCachedBytes').get('result'), description=f"[white]Mem cached   ", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemCachedBytes').get('result'))}")
                    self.progress_mem.update(self.task_mem_buffer, completed=node_mem_metrics_json.get('MemBuffersBytes').get('result'), description=f"[white]Mem buffer   ", total=node_mem_metrics_json.get('MemTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemBuffersBytes').get('result'))}")

                    self.progress_swap.update(self.task_swap_total, completed=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), description=f"[white]Swap Total   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapTotalBytes').get('result'))}")
                    self.progress_swap.update(self.task_swap_free, completed=node_mem_metrics_json.get('MemSwapFreeBytes').get('result'), description=f"[white]Swap free   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapFreeBytes').get('result'))}")
                    self.progress_swap.update(self.task_swap_cached, completed=node_mem_metrics_json.get('MemSwapCachedBytes').get('result'), description=f"[white]Swap cached   ", total=node_mem_metrics_json.get('MemSwapTotalBytes').get('result'), status=f"{helper_.bytes_to_kb_mb_gb(node_mem_metrics_json.get('MemSwapCachedBytes').get('result'))}")

                    self.progress_cpu_used_avg.update(self.task_cpu_used_avg, completed=(node_cpu_metrics_json.get('cpuUsageAVG').get('result') / 2), description=f"[white]CPU used AVG[10m]  ", total=100, status="")
                    self.progress_cpu.update(self.task_cpu_load1avg, description=f"[white]CPU load avg 1m   ", status=node_cpu_metrics_json.get('cpuLoadAvg1m').get('result'))
                    self.progress_cpu.update(self.task_cpu_load5avg, description=f"[white]CPU load avg 5m   ", status=node_cpu_metrics_json.get('cpuLoadAvg5m').get('result'))
                    self.progress_cpu.update(self.task_cpu_load15avg, description=f"[white]CPU load avg 15m   ", status=node_cpu_metrics_json.get('cpuLoadAvg15m').get('result'))

                    self.progress_fs_total.update(self.task_fs_size_total, description=f"[white]FS Total        ", status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsSize').get('result')))
                    self.progress_fs.update(self.task_fs_used, completed=node_fs_metrics_json.get('nodeFsUsed').get('result'), description=f"[white]FS used   ", total=node_fs_metrics_json.get('nodeFsSize').get('result'), status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsUsed').get('result')))
                    self.progress_fs.update(self.task_fs_available, completed=node_fs_metrics_json.get('nodeFsAvailable').get('result'), description=f"[white]FS available   ", total=node_fs_metrics_json.get('nodeFsSize').get('result'), status=helper_.bytes_to_kb_mb_gb(node_fs_metrics_json.get('nodeFsAvailable').get('result')))
                    
                    Logging.log.debug(f"Waiting for interval '{GlobalAttrs.live_update_interval}' before the next update")
                    time.sleep(GlobalAttrs.live_update_interval)

            def check_thread_node_resources(self, restart=True):
                while True:
                    def thread_status():
                        status = ""
                        if self.thread_node_resources.is_alive():
                            status = f"alive [green]✔️"
                        else:
                            status = "dead [red]❌"
                            if restart:
                                # Restart thread
                                self.start_threads()
                        return status

                    self.progress_threads_status.update(task_id=self.task_thread_refresh, status=thread_status())                            
                    time.sleep(5)
            
            class ValidatePrometheuesConnection(PrometheusNodeMetrics):
                def __init__(self):
                    super().__init__()
                    self.result = {}

                def run(self):
                    while True:
                        time.sleep(5)
                        self.result = self.verify_prometheus_connection()
                        if GlobalAttrs.debug:
                            print("DEBUG -- Function: ValidatePrometheuesConnection")
                        Logging.log.info("Function: ValidatePrometheuesConnection")
                        Logging.log.info("Function: ValidatePrometheuesConnection, waiting for internal '5s' ")

            def check_thread_prometheus_server_connection(self):
                while True:

                    def thread_status():
                        result = self.vlaidate_prometheus_server.result
                        # if self.thread_check_thread_prometheus_server_connection.is_alive():
                        if result.get('connected') is None:
                            status = f"waiting [green]✔️"
                        elif result.get('connected'):
                            status = f"connected [green]✔️"
                        else:
                            status = f"{result.get('reason')} [red]❌"

                        return status
                    
                    self.progress_threads_status.update(task_id=self.task_prometheus_server_connection, status=f"{thread_status()} ({self.vlaidate_prometheus_server.result.get('status_code')})")
                    time.sleep(5)

            def start_threads(self):
                self.thread_node_resources = threading.Thread(target=self.update)
                self.thread_node_resources.daemon = True
                self.thread_node_resources.start()
                Logging.log.debug("Started Thread: thread_node_resources")
                
                self.vlaidate_prometheus_server = self.ValidatePrometheuesConnection()
                self.thread_prometheus_server_connection = threading.Thread(target=self.vlaidate_prometheus_server.run)
                self.thread_prometheus_server_connection.daemon = True
                self.thread_prometheus_server_connection.start()
                Logging.log.debug("Started Thread: thread_prometheus_server_connection")

            def watch_threads(self):
                self.thread_check_thread_node_resources = threading.Thread(target=self.check_thread_node_resources)
                self.thread_check_thread_node_resources.daemon = True
                self.thread_check_thread_node_resources.start()

                self.thread_check_thread_prometheus_server_connection = threading.Thread(target=self.check_thread_prometheus_server_connection)
                self.thread_check_thread_prometheus_server_connection.daemon = True
                self.thread_check_thread_prometheus_server_connection.start()


        try:
            # node_metrics = PrometheusNodeMetrics()
            node_resources_progress = Node_Resources_Progress()

            progress_table = Table.grid(expand=True)
            progress_table.add_row(
                Panel(node_resources_progress.group_cpu, title="[b]CPU", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.group_memory, title="[b]Memory", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.group_fs, title='[b]FS "/"', padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(node_resources_progress.progress_threads_status, title="[b]Threads Status",padding=(1, 2), subtitle=""),
            )
            


            layout = make_layout()
            layout["header"].update(Header())
            # layout["body1_a"].update(progress_table)


            # layout["body2_a"].update(Panel("Loading ...", title="[b]Top Pods in Memory Usage", padding=(1, 1)))
            
            node_resources_progress.start_threads()
            node_resources_progress.watch_threads()

            update_disk_read_bytes_graph = True
            disk_read_bytes_graph = AsciiGraph()
            disk_read_bytes = self.nodeDiskReadBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'disk_read_bytes' metrics; Result:\n{disk_read_bytes}")
            else:
                Logging.log.info("Getting Pod 'disk_read_bytes' metrics")   
            if disk_read_bytes.get('success'):
                disk_read_bytes_graph.create_graph(disk_read_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                disk_read_bytes_graph.graph = disk_read_bytes.get('fail_reason')
                update_disk_read_bytes_graph = False

            update_network_received_bytes_graph = True
            network_received_bytes_graph =  AsciiGraph()
            network_received_bytes = self.nodeNetworkReceiveBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'network_received_bytes' metrics; Result:\n{network_received_bytes}")
            else:
                Logging.log.info("Getting Pod 'network_received_bytes' metrics")   
            if network_received_bytes.get('success'):
                network_received_bytes_graph.create_graph(network_received_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                network_received_bytes_graph.graph = network_received_bytes.get('fail_reason')
                update_network_received_bytes_graph = False

            update_network_transmit_bytes_graph = True
            network_transmit_bytes_graph =  AsciiGraph()
            network_transmit_bytes = self.nodeNetworkTransmitBytes(node_name)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'network_transmit_bytes' metrics; Result:\n{network_transmit_bytes}")
            else:
                Logging.log.info("Getting Pod 'network_transmit_bytes' metrics")   
            if network_transmit_bytes.get('success'):
                network_transmit_bytes_graph.create_graph(network_transmit_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                network_transmit_bytes_graph.graph = network_transmit_bytes.get('fail_reason')
                update_network_transmit_bytes_graph = False



            update_disk_written_bytes_graph = True
            disk_written_bytes_graph = AsciiGraph()
            disk_written_bytes = self.nodeDiskWrittenBytes(node_name)
            if disk_written_bytes.get('success'):
                disk_written_bytes_graph.create_graph(disk_written_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width, format='{:8.0f} kb/s')
            else:
                disk_written_bytes_graph.graph = disk_written_bytes.get('fail_reason')
                update_disk_written_bytes_graph = False

            # layout["body2_b_b"].update(Panel(Markdown("Loading ..."), title="[b]Network IO", padding=(1, 1)))
            # layout["body2_b_a"].update(Panel(Markdown("Loading ..."), title="[b]Disk IO", padding=(1, 1)))

            group_network_io = Group(
                Markdown("Bytes Received", justify='center'),
                Text.from_ansi(network_received_bytes_graph.graph + f"\n {network_received_bytes_graph.colors_description_str}"),
                Rule(style='#AAAAAA'),
                Markdown("Bytes Transmitted", justify='center'),
                Text.from_ansi(network_transmit_bytes_graph.graph + f"\n {network_transmit_bytes_graph.colors_description_str}")
            )

            group_disk_io = Group(
                Markdown("Bytes Read", justify='center'),
                Text.from_ansi(disk_read_bytes_graph.graph + f"\n {disk_read_bytes_graph.colors_description_str}"),
                Rule(style='#AAAAAA'),
                Markdown("Bytes Written", justify='center'),
                Text.from_ansi(disk_written_bytes_graph.graph + f"\n {disk_written_bytes_graph.colors_description_str}")
            )

            Logging.log.info("Starting the Layout.")
            with Live(layout, auto_refresh=True, screen=True, refresh_per_second=GlobalAttrs.live_update_interval):
                while True:
                    # pod_memory_usage = node_metrics.PodMemTopUsage(node=node_name)
                    # layout["body2_a"].update(Panel(pod_memory_usage, title="[b]Top Pods in Memory Usage", padding=(1, 1)))                    
                    # Logging.log.info("Updating the Layout with 'Top Pods in Memory Usage'")
                    # Logging.log.info(f"Result:\n{pod_memory_usage}")
                    
                    # if update_network_received_bytes_graph:
                    #     network_received_bytes = self.nodeNetworkReceiveBytes(node_name)
                    #     Logging.log.info("Updating Node 'network_received_bytes' metrics")
                    #     Logging.log.info(network_received_bytes)
                    #     for device, value in network_received_bytes.get('result').items():
                    #         network_received_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    # if update_network_transmit_bytes_graph:
                    #     Logging.log.info("Updating Node 'network_transmit_bytes' metrics")
                    #     Logging.log.info(network_transmit_bytes)
                    #     network_transmit_bytes = self.nodeNetworkTransmitBytes(node_name)
                    #     for device, value in network_transmit_bytes.get('result').items():
                        #         network_transmit_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))
                    
                    # if update_disk_read_bytes_graph:
                    #     disk_read_bytes = self.nodeDiskReadBytes(node_name)
                    #     Logging.log.info("Updating Node 'disk_read_bytes' metrics")
                    #     Logging.log.info(disk_read_bytes)
                    #     for device, value in disk_read_bytes.get('result').items():
                    #         disk_read_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    # if update_disk_written_bytes_graph:
                    #     disk_written_bytes = self.nodeDiskWrittenBytes(node_name)
                    #     Logging.log.info("Updating Node 'disk_written_bytes' metrics")
                    #     Logging.log.info(disk_written_bytes)
                    #     for device, value in disk_written_bytes.get('result').items():
                    #         disk_written_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    # if update_network_received_bytes_graph or update_network_transmit_bytes_graph:
                    #     group_network_io = Group(
                    #         Markdown("Bytes Received", justify='center'),
                    #         Text.from_ansi(network_received_bytes_graph.graph + f"\n {network_received_bytes_graph.colors_description_str}"),
                    #         Rule(style='#AAAAAA'),
                    #         Markdown("Bytes Transmitted", justify='center'),
                    #         Text.from_ansi(network_transmit_bytes_graph.graph + f"\n {network_transmit_bytes_graph.colors_description_str}")
                    #     )

                    # if update_disk_read_bytes_graph or update_disk_written_bytes_graph:
                    #     group_disk_io = Group(
                    #         Markdown("Bytes Read", justify='center'),
                    #         Text.from_ansi(disk_read_bytes_graph.graph + f"\n {disk_read_bytes_graph.colors_description_str}"),
                    #         Rule(style='#AAAAAA'),
                    #         Markdown("Bytes Written", justify='center'),
                    #         Text.from_ansi(disk_written_bytes_graph.graph + f"\n {disk_written_bytes_graph.colors_description_str}")
                    #     )

                    # layout["body2_b_b"].update(Panel(group_network_io, title="[b]Network IO", padding=(1, 1)))
                    # layout["body2_b_a"].update(Panel(group_disk_io, title="[b]Disk IO", padding=(1, 1)))

                    Logging.log.info(f"waiting for the update interval '{GlobalAttrs.live_update_interval}' before updating the Layout ")
                    time.sleep(GlobalAttrs.live_update_interval)   
                    Logging.log.info(f"Updating the layout")

        except Exception as e:
            rich.print("\n[yellow]ERROR -- " + str(e))
            rich.print("\n[underline bold]Exception:")
            traceback.print_exc()
            exit(1)
        except KeyboardInterrupt:
            print("                 ", end="\r")
            rich.print("Ok")
            exit(0)


    def node_monitor_dashboard_memory(self, node_name):
        print("not implemented yet.")
        exit(0)




