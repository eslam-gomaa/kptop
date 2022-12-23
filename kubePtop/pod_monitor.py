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
from kubePtop.ascii_graph import AsciiGraph
from kubePtop.colors import Bcolors
bcolors = Bcolors()


# from kubePtop.global_attrs import GlobalAttrs
from kubePtop.pod_metrics import PrometheusPodsMetrics
from kubePtop.helper import Helper
helper_ = Helper()
from kubePtop.logging import Logging


class Pod_Monitoring(PrometheusPodsMetrics):
    def __init__(self):
        super().__init__()

    def pod_monitor(self, pod, node=".*", container=".*", namespace="default"):
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
            layout["body"].split_row(Layout(name="body1", size=55), Layout(name="body2"),) # , Layout(name="box2")
            layout['body1'].split_column(Layout(name="body1_a"), Layout(name="body1_b", size=11))

            layout["body2"].split(Layout(name="body2_a", ratio=1), Layout(name="body2_b", ratio=1)) # , Layout(name="box2")
            layout['body2_b'].split_row(Layout(name="body2_b_a", ratio=1), Layout(name="body2_b_b", ratio=1))
            layout['body2_a'].split_row(Layout(name="body2_a_a", ratio=1), Layout(name="body2_a_b", ratio=1))

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
                    f"[b]Pod: [/b] {pod}   [b]Namespace: [/b] {namespace}   [b]Container: [/b] {container}",
                    datetime.now().ctime().replace(":", "[blink]:[/]"),
                )
                return Panel(grid, style="green")

        class Pod_Resources_Progress(PrometheusPodsMetrics):
            def __init__(self):
                super().__init__()
                self.mem_total_bytes = 0
                self.cpu_limit = 0
                self.progress_start()

            def progress_start(self):
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
                self.task_mem_total = self.progress_mem_total.add_task(description=f"[white]Mem Limit      ", status=" Loading")

                self.progress_mem = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                self.task_mem_used = self.progress_mem.add_task(completed=0, description=f"[white]Mem used   ", total=self.mem_total_bytes, status="Loading")                    
                self.task_mem_used_max = self.progress_mem.add_task(completed=0, description=f"[white]Mem used max   ", total=self.mem_total_bytes, status="Loading")               
                self.task_mem_cached = self.progress_mem.add_task(completed=0, description=f"[white]Mem cached   ", total=self.mem_total_bytes, status="Loading")
               
               
                self.progress_cpu_load_avg = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=20),
                    # TextColumn("[progress.percentage]{task.percentage:>3.0f}"),
                    TextColumn("{task.fields[status]}"),
                )
                self.task_cpu_limit = self.progress_cpu_load_avg.add_task(description=f"[white]CPU Limit   ", status="Loading")
                self.task_cpu_load_avg_10s = self.progress_cpu_load_avg.add_task(description=f"[white]CPU load avg 10s", status="Loading")
                               

                self.progress_cpu = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                self.task_cpu_used = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used TOTAL   ", total=100, status="Loading")
                self.task_cpu_used_system = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used SYS   ", total=100, status="Loading")                
                self.task_cpu_used_user = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used USER   ", total=100, status="Loading")
                
                self.progress_extra = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=16), 
                                                        # TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )
                self.task_extra_uptime = self.progress_extra.add_task(completed=0, description=f"[white]UP Time   ", total=100, status="Loading")
                start_time_json = self.podStartTime(pod=pod, namespace=namespace, container=container)
                if start_time_json.get('success'):
                    start_time = helper_.convert_epoch_timestamp(start_time_json.get('result'))
                else:
                    start_time = start_time_json.get('fail_reason')
                self.task_extra_start_time = self.progress_extra.add_task(completed=0, description=f"[white]Start Time   ", total=100, status=start_time)
                self.task_extra_file_discriptors = self.progress_extra.add_task(completed=0, description=f"[white]File Descriptors   ", total=100, status="Loading")
                self.task_extra_threads = self.progress_extra.add_task(completed=0, description=f"[white]Threads   ", total=100, status="Loading")
                self.task_extra_processes = self.progress_extra.add_task(completed=0, description=f"[white]Processes   ", total=100, status="Loading")


                self.group_memory = Group (
                    self.progress_mem_total,
                    self.progress_mem,
                    # Rule(style='#AAAAAA'),
                    # self.progress_swap,
                )

                self.group_cpu = Group (
                    self.progress_cpu_load_avg,
                    Rule(style='#AAAAAA'),
                    self.progress_cpu,
                )

            def update(self):
                time.sleep(3)
                while True:
                    try:
                        pod_metrics_json = self.podMetrics(pod, node, container, namespace)
                        pod_mem_metrics_json = pod_metrics_json.get('memory')
                        pod_cpu_metrics_json = pod_metrics_json.get('cpu')

                        ## Update Memory progress bars.
                        if pod_mem_metrics_json.get('MemLimitBytes').get('success'):
                            if pod_mem_metrics_json.get('MemLimitBytes').get('result') != 0:
                                self.progress_mem_total.update(task_id=self.task_mem_total, description=f"[white]Mem Limit      ", status=f"   {helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemLimitBytes').get('result'))}")
                                self.mem_total_bytes = pod_mem_metrics_json.get('MemLimitBytes').get('result')
                            else:
                                self.progress_mem_total.update(task_id=self.task_mem_total, description=f"[white]Mem Limit      ", status=f"    NO_LIMIT")
                        else:
                            self.progress_mem_total.update(task_id=self.task_mem_total, description=f"[white]Mem Limit      ", status=pod_mem_metrics_json.get('MemLimitBytes').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1


                        if pod_mem_metrics_json.get('MemUsageBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_used, completed=pod_mem_metrics_json.get('MemUsageBytes').get('result'), description=f"[white]Mem used   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemUsageBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_used, completed=0, description=f"[white]Mem used   ", total=100, status=pod_mem_metrics_json.get('MemUsageBytes').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1


                        if pod_mem_metrics_json.get('MemUsageMaxBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_used_max, completed=pod_mem_metrics_json.get('MemUsageMaxBytes').get('result'), description=f"[white]Mem used max   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemUsageMaxBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_used_max, completed=0, description=f"[white]Mem used max   ", total=100, status=pod_mem_metrics_json.get('MemUsageMaxBytes').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1               


                        if pod_mem_metrics_json.get('MemCachedBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_cached, completed=pod_mem_metrics_json.get('MemCachedBytes').get('result'), description=f"[white]Mem cached   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemCachedBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_cached, completed=0, description=f"[white]Mem cached   ", total=100, status=pod_mem_metrics_json.get('MemCachedBytes').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1
                
                        

                        ## Update CPU progress bars.
                        if pod_cpu_metrics_json.get('cpuLoadAvg10s').get('success'):
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", status=f" {pod_cpu_metrics_json.get('cpuLoadAvg10s').get('result')}")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", status=pod_cpu_metrics_json.get('cpuLoadAvg10s').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1

                        if pod_cpu_metrics_json.get('cpuQuotaMilicores').get('success'):
                            self.cpu_limit = pod_cpu_metrics_json.get('cpuQuotaMilicores').get('result')
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_limit, description=f"[white]CPU Limit   ", total=self.cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuQuotaMilicores').get('result')}m")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_limit, description=f"[white]CPU Limit   ", total=self.cpu_limit, status=" NO_LIMIT")

                        if pod_cpu_metrics_json.get('cpuLoadAvg10s').get('success'):
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", total=self.cpu_limit, status=f" {pod_cpu_metrics_json.get('cpuLoadAvg10s').get('result')}")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", total=self.cpu_limit, status=pod_cpu_metrics_json.get('cpuLoadAvg10s').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1
                                    

                        if pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used, completed=pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('result'), description=f"[white]CPU used TOTAL   ", total=self.cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used, completed=0, description=f"[white]CPU used TOTAL   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1
                        
                        if pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used_system, completed=pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('result'), description=f"[white]CPU used SYS   ", total=self.task_cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used_system, completed=0, description=f"[white]CPU used SYS   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1
                        
                        if pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used_user, completed=pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('result'), description=f"[white]CPU used USER   ", total=self.task_cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used_user, completed=0, description=f"[white]CPU used USER   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('fail_reason'))
                            GlobalAttrs.exceptions_num +=1

                        
                        # Update Extra progress bars
                        pod_uptime_json = self.podUpTime(pod=pod, container=container, namespace=namespace)
                        if pod_uptime_json.get('success'):
                            self.progress_extra.update(task_id=self.task_extra_uptime, completed=0, description=f"[white]UP Time   ", total=100, status=helper_.sec_to_m_h_d(pod_uptime_json.get('result')))
                            pass
                        else:
                            self.progress_extra.update(task_id=self.task_extra_uptime, completed=0, description=f"[white]UP Time   ", total=100, status=pod_uptime_json.get('fail_reason'))

                        pod_file_descriptors_json = self.podFileDescriptors(pod=pod, container=container, namespace=namespace)
                        if pod_file_descriptors_json.get('success'):
                            self.progress_extra.update(task_id=self.task_extra_file_discriptors, completed=0, description=f"[white]File Descriptors   ", total=100, status=int(pod_file_descriptors_json.get('result')))
                            pass
                        else:
                            self.progress_extra.update(task_id=self.task_extra_file_discriptors, completed=0, description=f"[white]File Descriptors   ", total=100, status=pod_file_descriptors_json.get('fail_reason'))
                        
                        pod_threads_json = self.podThreads(pod=pod, container=container, namespace=namespace)
                        if pod_threads_json.get('success'):
                            self.progress_extra.update(task_id=self.task_extra_threads, completed=0, description=f"[white]Threads   ", total=100, status=int(pod_threads_json.get('result')))
                        else:
                            self.progress_extra.update(task_id=self.task_extra_threads, completed=0, description=f"[white]Threads   ", total=100, status=pod_threads_json.get('fail_reason'))

                        pod_processes_json = self.podProcesses(pod=pod, container=container, namespace=namespace)
                        if pod_processes_json.get('success'):
                            self.progress_extra.update(task_id=self.task_extra_processes, completed=0, description=f"[white]Processes   ", total=100, status=int(pod_processes_json.get('result')))
                        else:
                            self.progress_extra.update(task_id=self.task_extra_processes, completed=0, description=f"[white]Processes   ", total=100, status=pod_processes_json.get('fail_reason'))


                        time.sleep(GlobalAttrs.live_update_interval)
                    except Exception as e:
                        Logging.log.error("Got an Exception while updating Progress Bars:")
                        Logging.log.error(e)
                        Logging.log.exception(traceback.format_stack())

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
                    time.sleep(GlobalAttrs.live_update_interval)
            
            class ValidatePrometheuesConnection(PrometheusPodsMetrics):
                def __init__(self):
                    super().__init__()
                    self.result = {}

                def run(self):
                    while True:
                        self.result = self.verify_prometheus_connection()
                        time.sleep(5)

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
                
                self.vlaidate_prometheus_server = self.ValidatePrometheuesConnection()
                self.thread_prometheus_server_connection = threading.Thread(target=self.vlaidate_prometheus_server.run)
                self.thread_prometheus_server_connection.daemon = True
                self.thread_prometheus_server_connection.start()

            def watch_threads(self):
                self.thread_check_thread_node_resources = threading.Thread(target=self.check_thread_node_resources)
                self.thread_check_thread_node_resources.daemon = True
                self.thread_check_thread_node_resources.start()

                self.thread_check_thread_prometheus_server_connection = threading.Thread(target=self.check_thread_prometheus_server_connection)
                self.thread_check_thread_prometheus_server_connection.daemon = True
                self.thread_check_thread_prometheus_server_connection.start()




        try:
            pod_resources_progress = Pod_Resources_Progress()

            progress_table = Table.grid(expand=True)
            progress_table.add_row(
                Panel(pod_resources_progress.group_cpu, title="[b]CPU", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(pod_resources_progress.group_memory, title="[b]Memory", padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(pod_resources_progress.progress_extra, title='[b]Extra', padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(pod_resources_progress.progress_threads_status, title="[b]Threads Status",padding=(1, 2), subtitle=""),
            )

            layout = make_layout()
            layout["header"].update(Header())
            layout["body1_a"].update(progress_table)
            layout['body1_b'].update(Panel("Made with [red]❤️[/red]", title='[b]Unused Space', padding=(1, 2),))

            pod_resources_progress.start_threads()
            pod_resources_progress.watch_threads()

            update_network_received_bytes_graph = True
            network_received_bytes_graph =  AsciiGraph()
            update_network_transmit_bytes_graph = True
            network_transmit_bytes_graph =  AsciiGraph()
            network_received_bytes = self.podNetworkReceiveBytes(pod, namespace=namespace)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'network_received_bytes' metrics; Result:\n{network_received_bytes}")
            else:
                Logging.log.info("Getting Pod 'network_received_bytes' metrics")
            if network_received_bytes.get('success'):
                network_received_bytes_graph.create_graph(network_received_bytes.get('result').keys(), height=6, width=GlobalAttrs.graphs_width -3, format='{:8.0f} kb/s')
                network_transmit_bytes_graph.create_graph(network_received_bytes.get('result').keys(), height=6, width=GlobalAttrs.graphs_width -3, format='{:8.0f} kb/s')

            else:
                network_received_bytes_graph.graph = network_received_bytes.get('fail_reason')
                update_network_received_bytes_graph = False
                network_transmit_bytes_graph.graph = network_received_bytes.get('fail_reason')
                update_network_transmit_bytes_graph = False
                

            # update_network_transmit_bytes_graph = True
            # network_transmit_bytes_graph =  AsciiGraph()
            # network_transmit_bytes = self.podNetworkTransmitBytes(pod, namespace=namespace)
            # Logging.log.info("Getting Pod 'network_transmit_bytes' metrics")
            # Logging.log.info(network_transmit_bytes)
            # if network_transmit_bytes.get('success'):
            #     network_transmit_bytes_graph.create_graph(network_transmit_bytes.get('result').keys(), height=6, width=42, format='{:8.0f} kb/s')
            # else:
            #     network_transmit_bytes_graph.graph = network_transmit_bytes.get('fail_reason')
            #     update_network_transmit_bytes_graph = False


            update_disk_read_bytes_graph = True
            update_disk_write_bytes_graph = True
            disk_read_bytes_graph = AsciiGraph()
            disk_write_bytes_graph = AsciiGraph()
            disk_read_bytes = self.podDiskReadBytes(pod=pod, container=container, namespace=namespace)
            if GlobalAttrs.debug:
                Logging.log.debug(f"Getting Pod 'disk_read_bytes' metrics; Result:\n{disk_read_bytes}")
            else:
                Logging.log.info("Getting Pod 'disk_read_bytes' metrics")
            if disk_read_bytes.get('success'):
                disk_read_bytes_graph.create_graph(disk_read_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width -3, format='{:8.0f} kb/s')
                disk_write_bytes_graph.create_graph(disk_read_bytes.get('result').keys(), height=5, width=GlobalAttrs.graphs_width -3, format='{:8.0f} kb/s')
            else:
                disk_read_bytes_graph.graph = disk_read_bytes.get('fail_reason')
                disk_write_bytes_graph.graph = disk_read_bytes.get('fail_reason')
                update_disk_read_bytes_graph = False
                update_disk_write_bytes_graph = False

            # update_disk_write_bytes_graph = True
            # disk_write_bytes_graph = AsciiGraph()
            # disk_write_bytes = self.podDiskWriteBytes(pod=pod, container=container, namespace=namespace)
            # Logging.log.info("Getting Pod 'disk_write_bytes' metrics")
            # Logging.log.info(disk_write_bytes)
            # if disk_write_bytes.get('success'):
            #     disk_write_bytes_graph.create_graph(disk_write_bytes.get('result').keys(), height=5, width=45, format='{:8.0f} kb/s')
            # else:
            #     disk_write_bytes_graph.graph = disk_write_bytes.get('fail_reason')
            #     update_disk_write_bytes_graph = False


            layout["body2_b_b"].update(Panel(Markdown("Loading ..."), title="[b]Network IO", padding=(1, 1)))
            layout["body2_b_a"].update(Panel(Markdown("Loading ..."), title="[b]Disk IO", padding=(1, 1)))

            update_containers_mem_usage = True
            containers_mem_usage_graph = AsciiGraph()
            containers_mem_usage_range_graph = AsciiGraph()
            containers_mem_usage = self.podMemUsagePerContainers(pod=pod, container=container, namespace=namespace)
            if containers_mem_usage.get('success'):
                containers_mem_usage_graph.create_graph(containers_mem_usage.get('result').keys(), height=5, width=GlobalAttrs.graphs_width - 3, format='{:8.0f} mb')
                containers_mem_usage_range_graph.create_graph(containers_mem_usage.get('result').keys(), height=5, width=GlobalAttrs.graphs_width -3, format='{:8.0f} mb')
            else:
                containers_mem_usage_graph.graph = containers_mem_usage.get('fail_reason')
                update_containers_mem_usage = False


            layout["body2_a_a"].update(Panel(Markdown("Loading ..."), title="[b]Memory Usage per Containers", padding=(1, 1)))
            
            group_mem_usage_per_containers = Group(
                Markdown("[CURRENT]", justify='center'),
                Text.from_ansi(containers_mem_usage_graph.graph + f"\n {containers_mem_usage_graph.colors_description_str}"),
                Rule(style='#AAAAAA'),
                Markdown("[LAST 3 HOURS]", justify='center'),
            )

        
            update_pod_pvcs_usage = True
            pod_pvcs_usage_graph = AsciiGraph()
            pod_pvcs = self.podPVC(pod, namespace)
            if pod_pvcs.get('success'):
                pod_pvcs_usage_graph.create_graph(pod_pvcs.get('result').keys(), height=6, width=GlobalAttrs.graphs_width, format='{:8.0f} mb')
            else:
                pod_pvcs_usage_graph.graph = f"{bcolors.BOLD + bcolors.WARNING} [ No PVCs found ]{bcolors.ENDC}\n{bcolors.GRAY}{pod_pvcs.get('fail_reason')}"
                update_pod_pvcs_usage = False

            layout["body2_a_b"].update(Panel(Markdown("Loading..."), title="[b]PVCs used by the pod", padding=(1, 1)))


            Logging.log.info("Starting the Layout.")
            with Live(layout, auto_refresh=True, screen=True, refresh_per_second=GlobalAttrs.live_update_interval):
                while True:

                    if update_containers_mem_usage:
                        containers_mem_usage = self.podMemUsagePerContainers(pod=pod, container=container, namespace=namespace)
                        for c, value in containers_mem_usage.get('result').items():
                            containers_mem_usage_graph.update_lst(c, helper_.bytes_to_mb(value))
                            containers_mem_usage_range = self.podMemUsagePerContainers_range(pod=pod, container=c, namespace=namespace)
                            containers_mem_usage_range_graph.replace_lst(c, containers_mem_usage_range.get('result'))

                    group_mem_usage_per_containers = Group(
                        Markdown("[CURRENT]", justify='center'),
                        Text.from_ansi(containers_mem_usage_graph.graph + f"\n {containers_mem_usage_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        Markdown("[LAST 3 HOURS]", justify='center'),
                        Text.from_ansi(containers_mem_usage_range_graph.graph + f"\n {containers_mem_usage_range_graph.colors_description_str}"),

                    )
                    layout["body2_a_a"].update(Panel(group_mem_usage_per_containers, title="[b]Memory Usage per Containers", padding=(1, 1)))


                    if update_pod_pvcs_usage:
                        pod_pvcs = self.podPVC(pod, namespace)
                        for pvc, value in pod_pvcs.get('result').items():
                            pod_pvcs_usage_graph.update_lst(pvc, helper_.bytes_to_mb(value.get('used')))

                    group_pod_pvcs = Group(
                        Text.from_ansi(pod_pvcs_usage_graph.graph + f"\n {pod_pvcs_usage_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        self.podPVC_table(pod, namespace)
                    )
                    layout["body2_a_b"].update(Panel(group_pod_pvcs, title="[b]PVCs used by the pod", padding=(1, 1)))
                    
                    
                    if update_network_received_bytes_graph:
                        network_received_bytes = self.podNetworkReceiveBytes(pod, namespace)
                        if GlobalAttrs.debug:
                            Logging.log.debug(f"Getting Pod 'network_received_bytes' metrics; Result:\n{network_received_bytes}")
                        else:
                            Logging.log.info("Getting Pod 'network_received_bytes' metrics")                        
                        for device, value in network_received_bytes.get('result').items():
                            network_received_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    if update_network_transmit_bytes_graph:
                        network_transmit_bytes = self.podNetworkTransmitBytes(pod, namespace)
                        if GlobalAttrs.debug:
                            Logging.log.debug(f"Updating Pod 'network_transmit_bytes' metrics; Result:\n{network_transmit_bytes}")
                        else:
                            Logging.log.info("Updating Pod 'network_transmit_bytes' metrics")     
                        for device, value in network_transmit_bytes.get('result').items():
                            network_transmit_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    group_network_io = Group(
                        Markdown("Bytes Received", justify='center'),
                        Text.from_ansi(network_received_bytes_graph.graph + f"\n {network_received_bytes_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        Markdown("Bytes Transmitted", justify='center'),
                        Text.from_ansi(network_transmit_bytes_graph.graph + f"\n {network_transmit_bytes_graph.colors_description_str}"),
                    )
                    
                    layout["body2_b_b"].update(Panel(group_network_io, title="[b]Network IO", padding=(1, 1)))


                    if update_disk_read_bytes_graph:
                        disk_read_bytes = self.podDiskReadBytes(pod=pod, container=container, namespace=namespace)
                        if GlobalAttrs.debug:
                            Logging.log.debug(f"Updating Pod 'disk_read_bytes' metrics; Result:\n{disk_read_bytes}")
                        else:
                            Logging.log.info("Updating Pod 'disk_read_bytes' metrics")
                        for device, value in disk_read_bytes.get('result').items():
                            disk_read_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    if update_disk_write_bytes_graph:
                        disk_write_bytes = self.podDiskWriteBytes(pod=pod, container=container, namespace=namespace)
                        if GlobalAttrs.debug:
                            Logging.log.debug(f"Updating Pod 'disk_write_bytes' metrics; Result:\n{disk_write_bytes}")
                        else:
                            Logging.log.info("Updating Pod 'disk_write_bytes' metrics")
                        for device, value in disk_write_bytes.get('result').items():
                            disk_write_bytes_graph.update_lst(device, helper_.bytes_to_kb(value))

                    group_disk_io = Group(
                        Markdown("Bytes Read", justify='center'),
                        Text.from_ansi(disk_read_bytes_graph.graph + f"\n {disk_read_bytes_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        Markdown("Bytes Write", justify='center'),
                        Text.from_ansi(disk_write_bytes_graph.graph + f"\n {disk_write_bytes_graph.colors_description_str}"),
                    )
                    layout["body2_b_a"].update(Panel(group_disk_io, title="[b]Network IO", padding=(1, 1)))




                    
                    time.sleep(GlobalAttrs.live_update_interval)
        except Exception as e:
            rich.print("\n[yellow]ERROR -- " + str(e))
            rich.print("\n[underline bold]Exception:")
            traceback.print_exc()
            exit(1)
        except KeyboardInterrupt:
            print("                 ", end="\r")
            rich.print("Ok")
            if GlobalAttrs.exceptions_num > 0:
                print(f"Found {GlobalAttrs.exceptions_num} Exceptions, you can find the errors in the log file: {GlobalAttrs.log_file_path}")
            exit(0)



            