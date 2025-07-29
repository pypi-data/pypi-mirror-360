PING = '{"method": "PING"}'
PONG = '{"method": "PONG"}'


def subscription(params: list[str]) -> dict:
    return {
        "method": "SUBSCRIPTION",
        "params": params,
    }


def unsubscribe(params: list[str]) -> dict:
    return {
        "method": "UNSUBSCRIPTION",
        "params": params,
    }
