# Standard Library
from typing import List

# 1st Party Libraries
import mainstay
from mainstay.types.data import rent_estimates_response, rent_estimates_fetch_params

client = mainstay.Mainstay(
    # Set API key below or set the MAINSTAY_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[rent_estimates_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

# Type hints
address: rent_estimates_fetch_params.Address
result: rent_estimates_response.Result

for (address, result) in zip(addresses, client.data.rent_estimates.fetch(addresses=addresses)):
    print("input address:", address)
    print("token:", result.token)
    if result.rent_estimate:
        print("Estimated Rent Low:", result.rent_estimate.estimated_rent_low)
        print("Estimated Rent:", result.rent_estimate.estimated_rent)
        print("Estimated Rent High:", result.rent_estimate.estimated_rent_high)
    else:
        print("No rent estimate available for this address")
