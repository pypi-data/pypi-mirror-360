# Standard Library
from typing import List

# 1st Party Libraries
import mainstay
from mainstay.types.data import property_values_response, property_values_fetch_params

client = mainstay.Mainstay(
    # Set API key below or set the MAINSTAY_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[property_values_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

# Type hints
address: property_values_fetch_params.Address
result: property_values_response.Result

for (address, result) in zip(addresses, client.data.property_values.fetch(addresses=addresses)):
    print("Input address:", address)
    print("Token:", result.token)

    if result.property_value:
        print("Property value low:", result.property_value.value_low)
        print("Property value:", result.property_value.value)
        print("Property value high:", result.property_value.value_high)
    else:
        print("No property value available for this address")
