import argparse

from src.util.parser import load_parameters
from controller import Controller

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest='use_view', action='store_true', help="Use UI")
    parser.add_argument("-p", dest='param', help="Parameter File")
    parser.add_argument("-s", dest='seed', help='Random Seed')
    args = parser.parse_args()

    parameters = load_parameters(args.param, args.seed)
    parameters["USE_VIEW"] = args.use_view or parameters["USE_VIEW"]

    crtl = Controller(parameters=parameters)
    crtl.main_loop()

if __name__ == "__main__":
    main()
