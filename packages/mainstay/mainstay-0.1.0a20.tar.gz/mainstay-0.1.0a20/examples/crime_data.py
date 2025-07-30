# Standard Library
from typing import List

# 1st Party Libraries
import mainstay
from mainstay.types.data import crime_data_response, crime_data_fetch_params

client = mainstay.Mainstay(
    # Set API key below or set the MAINSTAY_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[crime_data_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

# Type hints
address: crime_data_fetch_params.Address
result: crime_data_response.Result

for (address, result) in zip(addresses, client.data.crime_data.fetch(addresses=addresses)):
    print("input address:", address)
    print("token:", result.token)

    if result:
        print("Output crime data:", result.model_dump_json(indent=2))
    else:
        print("No crime data available for this address.")
