from cgc.utils.config_utils import read_from_cfg


def load_user_api_keys():
    """Based on configuration getter creates pair of API keys

    :return: api_key and api_secret
    :rtype: list of strings
    """
    return read_from_cfg("api_key"), read_from_cfg("api_secret")


def load_user_cgc_secret():
    return read_from_cfg("cgc_secret")


def load_user_api_url():
    return read_from_cfg("cgc_api_url")
