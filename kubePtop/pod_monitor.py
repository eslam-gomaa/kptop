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


# from kubePtop.global_attrs import GlobalAttrs
from kubePtop.pod_metrics import PrometheusPodsMetrics
from kubePtop.helper import Helper
helper_ = Helper()
from kubePtop.logging import Logging


class Pod_Monitoring(PrometheusPodsMetrics):
    def __init__(self):
        super().__init__()

    def pod_monitor(self, pod, node=".*", container=".*"):
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
                    f"[b]Pod: [/b] {pod}     [b]Container: [/b] {container}",
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
                self.task_thread_refresh = self.progress_threads_status.add_task(description=f"[white]Interval Refresh", status=f"unknown")
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
                self.task_cpu_used = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used TOTAL AVG[10m]   ", total=100, status="Loading")
                self.task_cpu_used_system = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used SYS   AVG[10m]   ", total=100, status="Loading")                
                self.task_cpu_used_user = self.progress_cpu.add_task(completed=0, description=f"[white]CPU used USER  AVG[10m]   ", total=100, status="Loading")
                

                self.progress_pvc = Progress(TextColumn("[progress.description]{task.description}"),
                                                        BarColumn(bar_width=20), 
                                                        TaskProgressColumn(),
                                                        TextColumn("{task.fields[status]}"),
                                                        )

                self.task_pvc_i = self.progress_pvc.add_task(completed=0, description=f"[white]PVC Used   ", total=100, status="Loading")



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
                        pod_metrics_json = self.podMetrics(pod, node, container)
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
                            self.progress_mem_total.update(task_id=self.task_mem_total, description=f"[white]Mem Limit      ", status=pod_mem_metrics_json.get('MemLimitBytes').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1


                        if pod_mem_metrics_json.get('MemUsageBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_used, completed=pod_mem_metrics_json.get('MemUsageBytes').get('result'), description=f"[white]Mem used   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemUsageBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_used, completed=0, description=f"[white]Mem used   ", total=100, status=pod_mem_metrics_json.get('MemUsageBytes').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1


                        if pod_mem_metrics_json.get('MemUsageMaxBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_used_max, completed=pod_mem_metrics_json.get('MemUsageMaxBytes').get('result'), description=f"[white]Mem used max   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemUsageMaxBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_used_max, completed=0, description=f"[white]Mem used max   ", total=100, status=pod_mem_metrics_json.get('MemUsageMaxBytes').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1               


                        if pod_mem_metrics_json.get('MemCachedBytes').get('success'):
                            self.progress_mem.update(task_id=self.task_mem_cached, completed=pod_mem_metrics_json.get('MemCachedBytes').get('result'), description=f"[white]Mem cached   ", total=self.mem_total_bytes, status=f"{helper_.bytes_to_kb_mb_gb(pod_mem_metrics_json.get('MemCachedBytes').get('result'))}")
                        else:
                            self.progress_mem.update(task_id=self.task_mem_cached, completed=0, description=f"[white]Mem cached   ", total=100, status=pod_mem_metrics_json.get('MemCachedBytes').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1
                
                        

                        ## Update CPU progress bars.
                        if pod_cpu_metrics_json.get('cpuLoadAvg10s').get('success'):
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", status=f" {pod_cpu_metrics_json.get('cpuLoadAvg10s').get('result')}")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", status=pod_cpu_metrics_json.get('cpuLoadAvg10s').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1

                        if pod_cpu_metrics_json.get('cpuQuotaMilicores').get('success'):
                            self.cpu_limit = pod_cpu_metrics_json.get('cpuQuotaMilicores').get('result')
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_limit, description=f"[white]CPU Limit   ", total=self.cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuQuotaMilicores').get('result')}m")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_limit, description=f"[white]CPU Limit   ", total=self.cpu_limit, status=" NO_LIMIT")

                        if pod_cpu_metrics_json.get('cpuLoadAvg10s').get('success'):
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", total=self.cpu_limit, status=f" {pod_cpu_metrics_json.get('cpuLoadAvg10s').get('result')}")
                        else:
                            self.progress_cpu_load_avg.update(task_id=self.task_cpu_load_avg_10s, description=f"[white]CPU load avg 10s", total=self.cpu_limit, status=pod_cpu_metrics_json.get('cpuLoadAvg10s').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1
                                    

                        if pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used, completed=pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('result'), description=f"[white]CPU used TOTAL AVG[10m]   ", total=self.cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used, completed=0, description=f"[white]CPU used TOTAL AVG[10m]   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageAVG10mMilicores').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1
                        
                        if pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used_system, completed=pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('result'), description=f"[white]CPU used SYS   AVG[10m]   ", total=self.task_cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used_system, completed=0, description=f"[white]CPU used SYS   AVG[10m]   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageSystemAVG10mMilicores').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1
                        
                        if pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('success'):
                            self.progress_cpu.update(task_id=self.task_cpu_used_user, completed=pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('result'), description=f"[white]CPU used USER  AVG[10m]   ", total=self.task_cpu_limit, status=f"{pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('result')}m")
                        else:
                            self.progress_cpu.update(task_id=self.task_cpu_used_user, completed=0, description=f"[white]CPU used USER  AVG[10m]   ", total=100, status=pod_cpu_metrics_json.get('cpuUsageUserAVG10mMilicores').get('fail_reason')[:30] + "...")
                            GlobalAttrs.exceptions_num +=1


                        # pod_pvc_metrics_json = self.podPVC(pod)
                        



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
                Panel("", title='[b]Inodes"/"', padding=(1, 2)),
            )
            progress_table.add_row(
                Panel(pod_resources_progress.progress_threads_status, title="[b]Threads Status",padding=(1, 2), subtitle=""),
            )

            layout = make_layout()
            layout["header"].update(Header())
            layout["body1_a"].update(progress_table)

            pod_resources_progress.start_threads()
            pod_resources_progress.watch_threads()

            # update_disk_written_bytes_graph = True
            # disk_written_bytes_graph = AsciiGraph()
            # disk_written_bytes = self.nodeDiskWrittenBytes(node_name)
            # if disk_written_bytes.get('success'):
            #     disk_written_bytes_graph.create_graph(disk_written_bytes.get('result').keys(), height=5, width=45, format='{:8.0f} kb/s')
            # else:
            #     disk_written_bytes_graph.graph = disk_written_bytes.get('fail_reason')[:30] + "..."
            #     update_disk_written_bytes_graph = False
            

            update_containers_mem_usage = True
            containers_mem_usage_graph = AsciiGraph()
            containers_mem_usage = self.podMemUsagePerContainers(pod=pod, container=container)
            if containers_mem_usage.get('success'):
                containers_mem_usage_graph.create_graph(containers_mem_usage.get('result').keys(), height=5, width=40, format='{:8.0f} mb')
            else:
                containers_mem_usage_graph.graph = containers_mem_usage.get('fail_reason')[:30] + "..."
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
            pod_pvcs = self.podPVC(pod)
            if pod_pvcs.get('success'):
                pod_pvcs_usage_graph.create_graph(pod_pvcs.get('result').keys(), height=5, width=45, format='{:8.0f} mb')
            else:
                pod_pvcs_usage_graph.graph = pod_pvcs.get('fail_reason')
                update_pod_pvcs_usage = False

            layout["body2_a_b"].update(Panel(Markdown("Loading..."), title="[b]PVCs used by the pod", padding=(1, 1)))



            Logging.log.info("Starting the Layout.")
            with Live(layout, auto_refresh=True, screen=True, refresh_per_second=GlobalAttrs.live_update_interval):
                while True:

                    if update_containers_mem_usage:
                        containers_mem_usage = self.podMemUsagePerContainers(pod=pod, container=container)
                        for device, value in containers_mem_usage.get('result').items():
                            containers_mem_usage_graph.update_lst(device, helper_.bytes_to_mb(value))

                    group_mem_usage_per_containers = Group(
                        Markdown("[CURRENT]", justify='center'),
                        Text.from_ansi(containers_mem_usage_graph.graph + f"\n {containers_mem_usage_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        Markdown("[LAST 3 HOURS]", justify='center'),
                    )

                    if update_pod_pvcs_usage:
                        pod_pvcs = self.podPVC(pod)
                        for pvc, value in pod_pvcs.get('result').items():
                            pod_pvcs_usage_graph.update_lst(pvc, helper_.bytes_to_mb(value.get('used')))

                    group_pod_pvcs = Group(
                        Text.from_ansi(pod_pvcs_usage_graph.graph + f"\n {pod_pvcs_usage_graph.colors_description_str}"),
                        Rule(style='#AAAAAA'),
                        self.podPVC_table(pod)
                    )
                    
                    layout["body2_a_a"].update(Panel(group_mem_usage_per_containers, title="[b]Memory Usage per Containers", padding=(1, 1)))
                    layout["body2_a_b"].update(Panel(group_pod_pvcs, title="[b]PVCs used by the pod", padding=(1, 1)))

                     
                 
                    
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
                print(f"Found {GlobalAttrs.exceptions_num} Exception/s, you can find the errors in the log file: {GlobalAttrs.log_file_path}")
            exit(0)



            