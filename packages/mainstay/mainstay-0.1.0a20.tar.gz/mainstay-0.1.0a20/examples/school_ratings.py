# Standard Library
from typing import List

# 1st Party Libraries
import mainstay
from mainstay.types.data import school_ratings_response, school_ratings_fetch_params

client = mainstay.Mainstay(
    # Set API key below or set the MAINSTAY_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[school_ratings_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

# Type hints
address: school_ratings_fetch_params.Address
result: school_ratings_response.Result

for (address, result) in zip(addresses, client.data.school_ratings.fetch(addresses=addresses)):
    print("input address:", address)
    print("token:", result.token)

    if result:
        print("Output school ratings:", result.model_dump_json(indent=2))
    else:
        print("No school ratings available for this address.")
