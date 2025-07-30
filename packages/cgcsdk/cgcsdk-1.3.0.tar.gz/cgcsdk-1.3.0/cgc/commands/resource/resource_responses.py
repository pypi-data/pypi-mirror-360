from cgc.utils.message_utils import key_error_decorator_for_helpers


@key_error_decorator_for_helpers
def get_ingress_list_from_response(data: dict) -> list:
    return data["details"]["ingress"]
