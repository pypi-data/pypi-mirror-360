# Standard Library
import json
from typing import List

# Third-Party Libraries
import pydantic.json

# 1st Party Libraries
import mainstay
from mainstay.types.data import rental_comps_response, rental_comps_fetch_params

# TODO: Rename rental_comps_fetch_params -> rental_comps_fetch_params

client = mainstay.Mainstay(
    # Set API key below or set the MAINSTAY_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[rental_comps_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

filters: rental_comps_fetch_params.Filters = {
    "bedrooms_total": {
        "relative": 1,
    }
}

# Type hints
address: rental_comps_fetch_params.Address
result: rental_comps_response.Result

for (address, result) in zip(addresses, client.data.rental_comps.fetch(addresses=addresses, filters=filters)):
    print("input address:", address)
    print("token:", result.token)

    if result.subject_property_details:
        output_address = {
            "street": result.subject_property_details.street,
            "city": result.subject_property_details.city,
            "state": result.subject_property_details.state,
            "postal_code": result.subject_property_details.postal_code,
        }
        print("Output address:", output_address)
        print("Subject property details:", result.subject_property_details.model_dump_json(indent=2))
    print("Number of rental comps:", len(result.rental_comps))

    if result.rental_comps:
        print("Rental comps json:", json.dumps(result.rental_comps, indent=2, default=pydantic.json.pydantic_encoder))
        for index, rental_comp in enumerate(result.rental_comps):
            assert rental_comp.property_details
            print(f"Rental comp {index + 1}:")
            rental_comp_address = {
                "street": rental_comp.property_details.street,
                "city": rental_comp.property_details.city,
                "state": rental_comp.property_details.state,
                "postal_code": rental_comp.property_details.postal_code,
            }
            print("address:", rental_comp_address)
            print("close price:", rental_comp.close_price)
            print("close date:", rental_comp.close_price_date)
            print("distance miles:", rental_comp.distance_miles)
            print("dom:", rental_comp.dom)
            print("initial list price:", rental_comp.initial_list_price)
            print("initial list price date:", rental_comp.initial_list_price_date)
            print("last event date:", rental_comp.last_event_date)
            print("last list price:", rental_comp.last_list_price)
            print("listing status:", rental_comp.listing_status)
            print("move out date:", rental_comp.move_out_date)
            print("ownership profile:", rental_comp.ownership_profile)
            print("response codes:", rental_comp.response_codes)
            print("similarity score:", rental_comp.similarity_score, end="\n\n")
    else:
        print("No rental comps available for this address.")
