def run():
    # It runs at the initilization
    from kubePtop.cli import Cli


run()

# from kubePtop.node_metrics import PrometheusNodeMetrics
# from kubePtop.read_env import ReadEnv
# env = ReadEnv()
# env.read_env()
# import rich

# test = PrometheusNodeMetrics()
# rich.print(test.nodeManagedK8sInfo('.*'))
# print(test.topNode())
# test.topNodeTable(option="cloud")
# test.topNodeJson('ip-10-129-143-105.eu-west-1.compute.internal')


