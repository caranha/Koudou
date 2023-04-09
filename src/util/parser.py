from platform import system

def load_parameters(filename, seed):
    parameters = load_defaults()

    if filename is None:
        return parameters

    with open(filename, 'r') as file:
        tmp_params = "".join(file.readlines())

    ctx = {"parameters": dict()}
    try:
        exec(tmp_params, ctx)
    except SyntaxError:
        raise Exception("Invalid syntax in the parameter file.")

    for key in ctx["parameters"].keys():
        parameters[key] = ctx["parameters"][key]

    if seed is None:
        parameters['SEED'] = 999
    else:
        parameters['SEED'] = int(seed)

    return parameters

def load_defaults():
    parameters = {

        # EXPERIMENT
        "EXP_NAME": "default",
        "SEED"    : 3333,
        "MAX_STEPS"    :   49*24*12,


        # MAP
        "MAP":               None,
        "MAP_CACHE":         None,
        "PATHFIND_CACHE":    None,
        "BUILDING_TAGS":     None,
        "BUSINESS":          None,
        "GRID_SIZE":         20,

        # VIEW
        "USE_VIEW":         False,
        "ZOOM_IN":          1.1,
        "ZOOM_OUT":         (10.0/11.0),

        # SIMULATION
        "SIM_CONFIG":       None,
        "DISEASES":         None,
        "EVACUATION":       None,


        "OS": system(),

    }
    return parameters
