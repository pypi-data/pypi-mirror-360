# Miru Python SDK
This repository contains the [Miru](https://docs.miruml.com/) Python SDK for verifying Miru callbacks. 

## Installation

```sh
pip install miru-server-sdk
```

## Verify a Callback
Please refer to [the official documentation](https://docs.miruml.com/) for more usage instructions.

```python
from miru.webhooks import Webhook

secret = "cbsec_WrtItCFkZWrP8h9q4FgnoZsS3QlwUt3o/7juCWkGc1c="

# These were all sent from the server
headers = {
  "miru-id": "evt_p5jXN8AQM9LWM0D4loKWxJek",
  "miru-timestamp": "1614265330",
  "miru-signature": "v1,g0hM9SsE+OTPJTGt/tmIKtSyZlE3uFJELVlNIOLJ1OE=",
}
payload = '{"test": 2432232314}'

wh = Webhook(secret)
# Throws on error, returns the verified content on success
wh.verify(payload, headers)
```