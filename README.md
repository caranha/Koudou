# Koudou
Modular small community simulator

This repository contains the simulator used for the paper: Shiyu Jiang, Hee Joong Kim, Fabio Tanaka, Claus Aranha, 
Anna Bogdanova, Kimia Ghobadi and Anton Dahbura. 2023. [**Simulating Disease Spread During Disaster Scenarios**]() 
In Proceedings of the International Conference on Artificial Life (ALife 2023).

## How to reproduce the results:
### Set up environment
```
git clone -b ALIFE_2023 https://github.com/caranha/Koudou.git
cd Koudou
pip install -r requirements.txt
``` 
### Deploy Map .osm file
Download the .osm file for the tsukuba area and place it on: osm_files/Tx-To-TU.osm
- To download the file go to: https://www.openstreetmap.org/export and set the following coordinates:
  - minlat="36.0777000"
  - minlon="140.0921000" 
  - maxlat="36.1217000"
  - maxlon="140.1201000"
- Or download using the API req:
        https://www.openstreetmap.org/api/0.6/map?bbox=140.0921%2C36.0777%2C140.1201%2C36.1217
### Modify the config files
Referring to the directory of config and parameters, modify the files to the desired configuration as introduced in the
paper. Here is some default parameters as tables for reference:
#### Reduced infection rate for mask `config/infection/covid.json --> "precautionary_measures"`
The infection will multiply by the reduced infection rate based on agent's mask condition.

| Mask | Reduced Infection Rate |
| --- | --- |
| `No Mask` | 1.0 | 
| `Surgical Mask` | 0.34 |
| `N95 Mask` | 0.17 |
#### Chances of changing mask `config/infection/covid.json --> "precautionary_measures"`
When self-infected, the chance of changing mask to a better one.

| Condition | Current | Next | Chance |
| --- | --- | --- | --- |
| `Self infection masked` | Surgical mask | N95 | 0 |
| `Self infection masked` | No change | No change | 1 |
| `Self infection unmasked` | No mask | Surgical mask | 0 |
| `Self infection unmasked` | No mask | N95 | 0 |
| `Self infection unmasked` | No change | No change | 1 |
#### Agent profession with mask `/config/behavioral/profession.csv`
Proportion of agents with mask for each profession at initialization. The sum of the proportion of each profession should be 1.

| Profession | No mask | Surgical mask | N95 mask |
| --- | --- | --- | --- |
| `student` | 0.75 | 0.125 | 0.125 |
| `university student` | 0.75 | 0.125 | 0.125 |
| `teacher` | 0.75 | 0.125 | 0.125 |
| `medical doctor` | 0 | 0 | 1 |
| `teacher` | 0.75 | 0.125 | 0.125 |
| `university professor` | 0.75 | 0.125 | 0.125 |
| `salaryman outside city` | 0.75 | 0.125 | 0.125 |
| `retailer` | 0.75 | 0.125 | 0.125 |
| `salaryman` | 0.75 | 0.125 | 0.125 |
| `barber` | 0.75 | 0.125 | 0.125 |
| `restuarant worker` | 0.75 | 0.125 | 0.125 |
| `scientist` | 0.75 | 0.125 | 0.125 |


### Run the simulation
`-s`: seed for random number generator. It can help with the reproducibility of the results. If not specified, the
default seed is 1111.
```
python main.py -p parameters/default.py -s 1111
```
### Analyze the results
Use dashboard to analyze the results with visualization and statistics. It locates at `/src/dashapp/App.py`
Please refer to the `README.md` in the `dashapp` folder for more details.