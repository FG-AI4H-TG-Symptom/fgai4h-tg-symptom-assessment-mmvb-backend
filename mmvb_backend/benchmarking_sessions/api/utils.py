def strip_values_from_responses(responses):
    for case_responses in responses:
        for ai_implementation_id, response in case_responses[
            "responses"
        ].items():
            if "value" in response:
                del response["value"]
