# standard library imports
import base64
import hashlib
import hmac
import json
import typing as t
from datetime import datetime, timedelta, timezone
from math import floor


def hmac_data(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


class CallbackVerificationError(Exception):
    pass


class Callback:
    _SECRET_PREFIX: str = "cbsec_"
    _cbsecret: bytes

    def __init__(self, cbsecret: t.Union[str, bytes]):
        if not cbsecret:
            raise RuntimeError("Secret can't be empty.")

        if isinstance(cbsecret, str):
            if cbsecret.startswith(self._SECRET_PREFIX):
                cbsecret = cbsecret[len(self._SECRET_PREFIX) :]
            self._cbsecret = base64.b64decode(cbsecret)

        if isinstance(cbsecret, bytes):
            self._cbsecret = cbsecret

    def verify(self, data: t.Union[bytes, str], headers: t.Dict[str, str]) -> t.Any:
        data = data if isinstance(data, str) else data.decode()
        headers = {k.lower(): v for (k, v) in headers.items()}
        evt_id = headers.get("miru-id")
        evt_signature = headers.get("miru-signature")
        evt_timestamp = headers.get("miru-timestamp")
        if not (evt_id and evt_timestamp and evt_signature):
            raise CallbackVerificationError("Missing required headers")

        timestamp = self.__verify_timestamp(evt_timestamp)

        expected_sig = base64.b64decode(
            self.sign(evt_id=evt_id, timestamp=timestamp, data=data).split(",")[1]
        )
        passed_sigs = evt_signature.split(" ")
        for versioned_sig in passed_sigs:
            (version, signature) = versioned_sig.split(",")
            if version != "v1":
                continue
            sig_bytes = base64.b64decode(signature)
            if hmac.compare_digest(expected_sig, sig_bytes):
                return json.loads(data)

        raise CallbackVerificationError("No matching signature found")

    def sign(self, evt_id: str, timestamp: datetime, data: str) -> str:
        timestamp_str = str(floor(timestamp.replace(tzinfo=timezone.utc).timestamp()))
        to_sign = f"{evt_id}.{timestamp_str}.{data}".encode()
        signature = hmac_data(self._cbsecret, to_sign)
        return f"v1,{base64.b64encode(signature).decode('utf-8')}"

    def __verify_timestamp(self, timestamp_header: str) -> datetime:
        webhook_tolerance = timedelta(minutes=5)
        now = datetime.now(tz=timezone.utc)
        try:
            timestamp = datetime.fromtimestamp(float(timestamp_header), tz=timezone.utc)
        except Exception:
            raise CallbackVerificationError("Invalid Signature Headers")

        if timestamp < (now - webhook_tolerance):
            raise CallbackVerificationError("Message timestamp too old")
        if timestamp > (now + webhook_tolerance):
            raise CallbackVerificationError("Message timestamp too new")
        return timestamp
