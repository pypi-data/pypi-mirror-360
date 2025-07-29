import json
import requests
import logging
import pandas as pd

from typing import Optional


class Vavaprice_Helper():
    def __init__(self, url, token):
        """
        Vava price helper constructor.

        Parameters:
            url: Vava Price Engine endpoint
            bearer token:
        """
        self._url = url

        self._headers = {
            'Authorization': f'Bearer {token}'
            , 'Content-Type': 'application/json'
        }


    def get_quotation(self, car, debug=None, client: Optional[str] = None):
        """
        Gets an a quotation for a vehicle

        Parameters:
            car (pd.Series): vehicle details: year, make, model, bodytype, transmission, fueltype, trim, km, glassroof
                - make: string
                - model: string
                - year: integer
                - bodytype: string
                - transmission: string
                - fueltype: string
                - trim: string
                - km: integer
                - glassroof: boolean
            debug (boolean|str): if not False|None adds debug key in quotation request to retrieve prices of disabled make/model
            client (str): string to indicate which app is calling the Pricing Engine
        Returns:
            quotation (pd.Series): Columns:
                - adjmargin: Margin due to price adjusting (fix_price)
                - margin: Total margin (adjmargin + strategymargin + miscmargin)
                - discountpercentage: Total discount applied
                - strategymargin: Margin due just to strategy application
                - minprice: Initial offer price
                - miscmargin: Margin due to other factors (glassroof, temporary strategy, ..)
                - discounttype: "Camunda" or "CamundaError"
        """

        if client is None:
            client = debug if isinstance(debug, str) else 'unknown' # for compatibility with previous versions
            logging.warning(f"Should have specified a value for parameter 'client', setting '{client}' for now.")

        input_data = {
            "makename": car['make'],
            "modelname": car['model'],
            "body": car['bodytype'],
            "fuel": car['fueltype'],
            "transmission": car['transmission'],
            "trim": car['trim'],
            "year": car['year'],
            "mileage": car['km'],
            "glassroof": car.get('glassroof', 0),
            "client": client
        }

        if debug:
            input_data['debug'] = debug

        payload = json.dumps({"get_quotation": input_data})

        try:

            response = requests.request("POST", self._url, headers=self._headers, data=payload)
            response.raise_for_status()
            return pd.Series(json.loads(response.text))

        except Exception as e:
            logging.warning(f"Exception {e}: Couldnt get Vava price for {input_data}")
            return pd.Series({'retailprice': 0, 'ioprice': 0, 'strategy': 0, 'adjmargin': 0
                             , 'miscmargin': 0, 'discountpercentage': 0, 'discounttype': 'ERROR'
                             , 'input_data': input_data, 'debug': 'Error in Vavaprice_Helper', 'quote': 0})
