# import rich
# from kubePtop.node_monitor import Node_Monitoring
# from kubePtop.pod_monitor import Pod_Monitoring
# from kubePtop.pod_metrics import PrometheusPodsMetrics
# from kubePtop.node_metrics import PrometheusNodeMetrics
# from kubePtop.session import PrometheusAPI
# from kubePtop.read_env import ReadEnv
from kubePtop.cli import Cli

# import pdb
# pdb.set_trace()


# read_env = ReadEnv()

# sess = PrometheusAPI()
# node = Node_Monitoring()
# pod = PrometheusPodsMetrics()

# rich.print(pod.podMemUsagePerContainers(pod="prod-kafka-aws-cp-kafka-1"))


# print(sess.verify_prometheus_connection())

# rich.print(node.nodeNetworkReceiveBytes(node='ip-192-168-102-148.me-south-1.compute.internal'))

# metrics = PrometheusNodeMetrics()
# rich.print(metrics.PodMemTopUsage())
# rich.print(metrics.PodCpuUsageAvg())
# rich.print(metrics.NodeMemUsage_sorted_desc().get('result')[0].get('value')[1], [x.get('value') for x in metrics.NodeMemLimit().get('result') if x['metric']['pod'] == "prometheus-node-exporter-n9t5t" ])
# rich.print(metrics.NodeMemLimit().get('result'))


# rich.print(pod.PodMemUsage(pod="strimzi-kafka-entity-operator-68f6b965fc-qb4dx"))

# pod = Pod_Monitoring()

# cli = Cli()
