from kubePtop.read_env import ReadEnv
env = ReadEnv()
env.read_env()
from kubePtop.cli_args import Cli
cli = Cli()

def run():
    cli.run()
