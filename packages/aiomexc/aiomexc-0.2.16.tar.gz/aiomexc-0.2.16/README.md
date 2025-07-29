# aiomexc

Pretty and fully asynchronous wrapper for <a href="https://mexcdevelop.github.io/apidocs/spot_v3_en">MEXC API</a>.

## Using with HTTP API
You can start use wrapper very fast.

### Install

```sh
pip install aiomexc
```

You can install with protobuf dependencies to use WebSocket API

```sh
pip install aiomexc[ws]
```

- Import and initialize client.

```python
from aiomexc import MexcClient

client = MexcClient()
```

- Call needed method and get response as dataclass model.

```python
await client.get_ticker_price(symbol="BTCUSDT")
```

- To call methods that requires auth (e.g. open order), you can pass your credentils globally to client instance.

```python
from aiomexc import Credentials

client = MexcClient(credentials=Credentials(access_key="mx0.....", secret_key="......"))
```

Or if you need to make requests from different API credentials you can pass credentials to every method calls.

```python
await client.query_order(credentials=Credentials(access_key="mx0.....", secret_key="......"))
```

## TODO:
 - Support all methods
