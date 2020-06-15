def strip_values_from_responses(responses):
    """Strips `value` property if present within ai response for a case"""
    for case_responses in responses:
        for ai_implementation_id, response in case_responses[
            "responses"
        ].items():
            if "value" in response:
                del response["value"]
