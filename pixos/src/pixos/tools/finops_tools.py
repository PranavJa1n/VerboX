import boto3
import json
from pathlib import Path
import pandas as pd
from pixos.tools.check_instance import check_instance

         
def get_cloudwatch_metrics(instance_id : str):
    if(check_instance(instance_id) == -1):
        return
    else:
        return
        

            
        

if __name__ == '__main__':
    get_cloudwatch_metrics("id-11111")