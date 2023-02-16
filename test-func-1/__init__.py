import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Python 3
    def mult_numbers(a, b):
        return a * b
    # Unit test
    def test_mult_numbers():
        try:
            assert mult_numbers(3, 4) == 12
            return True
        except AssertionError:
            print("AssertionError")
            return False
       
    logging.info(f'Testing Function')
    logging.info(f'Start Function APP {test_mult_numbers()}')
    logging.info(f'Testing Function is DONE!~')
    
    first = req.params.get('first')
    sec = req.params.get('sec')
    if first and sec:
        res = mult_numbers(first, sec)

        if res:
            return func.HttpResponse(f"{res}",status_code=200)
        else:
            return func.HttpResponse(f"ERROR.",status_code=500)
    else:
        return func.HttpResponse('Please pass a first and sec on the query string or in the request body',status_code=200)