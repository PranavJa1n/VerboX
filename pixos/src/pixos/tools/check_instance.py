from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

def check_instance(instance_id : str):
    file = BASE_DIR.parent / 'localstack/instances/instances.csv'
    df = pd.read_csv(file)
    
    for row in df.itertuples(index=True):
        if(row.instance_id == instance_id):
            if(not(pd.isna(row.stop_time))):
                print("Instance Stopped at :", row.stop_time)
                return -1
            else:
                print("Fetched the instance : ", row.instance_id,", running from :", row.start_time)
                return row.instance_id
        else:
            print("Not exists")