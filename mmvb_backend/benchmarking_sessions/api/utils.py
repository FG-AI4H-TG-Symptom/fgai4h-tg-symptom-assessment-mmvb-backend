def strip_values_from_responses(responses):
    """Strips `value` property if present within ai response for a case"""
    for case_responses in responses:
        for ai_implementation_id, response in case_responses[
            "responses"
        ].items():
            if "value" in response:
                del response["value"]


def get_stats_table(responses, ai_ids):
    result = {}

    # create empties for collecting results
    for ai_id in ai_ids:
        result[ai_id] = {"errors": 0, "timeouts": 0, "completed": 0}

    # collect results
    for response in responses:
        responses_for_case = response["responses"]

        for ai_id in ai_ids:
            if responses_for_case[ai_id]["status"] == "COMPLETED":
                result[ai_id]["completed"] = result[ai_id]["completed"] + 1
            elif (
                responses_for_case[ai_id]["status"] == "ERRORED"
                and responses_for_case[ai_id]["error"] == "TIMEOUT"
            ):
                result[ai_id]["timeouts"] = result[ai_id]["timeouts"] + 1
            elif (
                responses_for_case[ai_id]["status"] == "ERRORED"
                and responses_for_case[ai_id]["error"] != "TIMEOUT"
            ):
                result[ai_id]["errors"] = result[ai_id]["errors"] + 1

    return result
