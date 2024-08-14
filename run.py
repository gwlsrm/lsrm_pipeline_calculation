import argparse

from create_graph import parse_config


def main():
    parser = argparse.ArgumentParser(description="runs computation graph")
    parser.add_argument("config_filename", help="input config with computation graph")
    args = parser.parse_args()

    graph = parse_config(args.config_filename)
    graph.run()
    print('done')


if __name__ == "__main__":
    main()
