def run():
    # It runs at the initilization
    from kubePtop.cli import Cli


# run()

from kubePtop.dashboard_monitor import customDashboardMonitoring
from kubePtop.read_env import ReadEnv
env = ReadEnv()
env.read_env()
import rich

test = customDashboardMonitoring()
rich.print(test.build_custom_dashboard("./dashboard.yaml"))
# rich.print(test.nodeManagedK8sInfo('.*'))
# print(test.topNode())
# test.topNodeTable(option="cloud")
# test.topNodeJson('ip-10-129-143-105.eu-west-1.compute.internal')
