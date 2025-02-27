import argparse
import json
from src.util.parser import load_parameters
from controller import Controller


JSON_FILE_PATH = "config/map/noto_evac.json"

# PLACE_ID_LIST = [
#     "1168915320","1236767271", "1236840494", "1236479782", "1236026407",
#     "1236467486", "1236249027",  "1236467484",
#     "1236838217", "1236887579"
# ]
PLACE_ID_LIST = [
    "1236504778"
]


def update_json_file(file_path, place_id):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "evacuation_centers" in data and data["evacuation_centers"]:
        data["evacuation_centers"][0]["rules"]["place_id"] = place_id

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest='use_view', action='store_true', help="Use UI")
    parser.add_argument("-p", dest='param', help="Parameter File")
    parser.add_argument("-s", dest='seed', help='Random Seed')
    parser.add_argument("-n", dest='num_runs', type=int, default=1, help="Number of times to run the program")

    args = parser.parse_args()

    parameters = load_parameters(args.param, args.seed)
    parameters["USE_VIEW"] = args.use_view or parameters["USE_VIEW"]

    for i in range(args.num_runs):
        print(f"Running iteration {i + 1}/{args.num_runs}...")

        if i < len(PLACE_ID_LIST):
            update_json_file(JSON_FILE_PATH, PLACE_ID_LIST[i])
        else:
            print("Warning: PLACE_ID_LIST 中的 place_id 已用完！")

        crtl = Controller(parameters=parameters)
        crtl.main_loop()

if __name__ == "__main__":
    main()
