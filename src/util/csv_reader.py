import csv

from src.util.paths import fromRoot

def read_csv_as_dict(file):
    datas = []
    with open(fromRoot(file)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        keys = []
        for row in csv_reader:
            data = {}
            if len(keys) == 0:
                keys = row
            elif len(row) != 0:         
                #print(row)
                for i in range(0,len(keys)):
                    data[keys[i]]=row[i]
                datas.append(data)
    return datas
                