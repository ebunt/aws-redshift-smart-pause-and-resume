import json
import boto3
import logging 
import datetime as dt
import os

from utils.forecast_helpers import derive_dataset_group_arn
from utils.forecast_helpers import derive_predictor_arn

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    DATASET_NAME = os.environ["DATASET_NAME"]
    DATASET_GROUP_NAME = os.environ["DATASET_GROUP_NAME"]
    ALGORITHM_ARN = os.environ["ALGORITHM_ARN"]
    FORECAST_HORIZON = int(os.environ["FORECAST_HORIZON"])
    FORECAST_FREQ = os.environ["FORECAST_FREQ"]
    PREDICTOR_NAME = "{0}_predictor{1}".format(DATASET_NAME, dt.datetime.now().strftime("%Y%m%d"))
    DATASET_GROUP_ARN = derive_dataset_group_arn(dataset_group_name = DATASET_GROUP_NAME, lambda_function_arn = context.invoked_function_arn)
    
    try:
        forecast_client = boto3.client("forecast", region_name="ap-southeast-2")
        
        forecast_client.create_predictor(
            PredictorName = PREDICTOR_NAME,
            AlgorithmArn = ALGORITHM_ARN,
            ForecastHorizon = FORECAST_HORIZON,
            PerformAutoML = False,
            PerformHPO = False,
            EvaluationParameters = {
                "NumberOfBacktestWindows": 1, 
                "BackTestWindowOffset": FORECAST_HORIZON
            },
            InputDataConfig = {
                "DatasetGroupArn": DATASET_GROUP_ARN, 
                "SupplementaryFeatures": [{
                    "Name": "holiday",
                    "Value": "AU"
                }]
            },
            FeaturizationConfig = {
                "ForecastFrequency": FORECAST_FREQ
            }
        )
    except forecast_client.exceptions.ResourceAlreadyExistsException as e:      
        logger.info("ResourceAlreadyExistsException: %s" % e)
    except Exception as e:
        logger.info("Exception: %s" % e)