import pytest
import base64
import typing as t
from math import floor
from datetime import datetime, timedelta, timezone

from miru_server_sdk.callbacks import hmac_data, Callback, CallbackVerificationError


defaultEvtID = "evt_p5jXN8AQM9LWM0D4loKWxJek"
defaultPayload = '{"test": 2432232314}'
defaultSecret = "MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"

tolerance = timedelta(minutes=5)


class PayloadForTesting:
    id: str
    timestamp: int
    payload: str
    secret: str
    signature: str
    header: t.Dict[str, str]

    def __init__(self, timestamp: datetime = datetime.now(tz=timezone.utc)):
        ts = floor(timestamp.timestamp())
        to_sign = f"{defaultEvtID}.{ts}.{defaultPayload}".encode()
        signature = base64.b64encode(
            hmac_data(base64.b64decode(defaultSecret), to_sign)
        ).decode("utf-8")

        self.id = defaultEvtID
        self.timestamp = ts
        self.payload = defaultPayload
        self.secret = defaultSecret
        self.signature = signature
        self.header = {
            "miru-id": defaultEvtID,
            "miru-signature": "v1," + signature,
            "miru-timestamp": str(self.timestamp),
        }


def test_missing_id_raises_error() -> None:
    testPayload = PayloadForTesting()
    del testPayload.header["miru-id"]

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_timestamp_raises_error() -> None:
    testPayload = PayloadForTesting()
    del testPayload.header["miru-timestamp"]

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_invalid_timestamp_raises_error() -> None:
    testPayload = PayloadForTesting()
    testPayload.header["miru-timestamp"] = "hello"

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_missing_signature_raises_error() -> None:
    testPayload = PayloadForTesting()
    del testPayload.header["miru-signature"]

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_invalid_signature_raises_error() -> None:
    testPayload = PayloadForTesting()
    testPayload.header["miru-signature"] = (
        "v1,g0hM9SsE+OTPJTGt/tmIKtSyZlE3uFJELVlNIOLJ1OA="
    )

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_valid_signature_is_valid_and_returns_json() -> None:
    testPayload = PayloadForTesting()

    cb = Callback(testPayload.secret)

    json = cb.verify(testPayload.payload, testPayload.header)
    assert json["test"] == 2432232314


def test_old_timestamp_fails() -> None:
    testPayload = PayloadForTesting(
        datetime.now(tz=timezone.utc) - tolerance - timedelta(seconds=1)
    )

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_new_timestamp_fails() -> None:
    testPayload = PayloadForTesting(
        datetime.now(tz=timezone.utc) + tolerance + timedelta(seconds=1)
    )

    cb = Callback(testPayload.secret)

    with pytest.raises(CallbackVerificationError):
        cb.verify(testPayload.payload, testPayload.header)


def test_multi_sig_payload_is_valid() -> None:
    testPayload = PayloadForTesting()
    sigs = [
        "v1,Ceo5qEr07ixe2NLpvHk3FH9bwy/WavXrAFQ/9tdO6mc=",
        "v2,Ceo5qEr07ixe2NLpvHk3FH9bwy/WavXrAFQ/9tdO6mc=",
        testPayload.header["miru-signature"],  # valid signature
        "v1,Ceo5qEr07ixe2NLpvHk3FH9bwy/WavXrAFQ/9tdO6mc=",
    ]
    testPayload.header["miru-signature"] = " ".join(sigs)

    cb = Callback(testPayload.secret)

    json = cb.verify(testPayload.payload, testPayload.header)
    assert json["test"] == 2432232314


def test_signature_verification_with_and_without_prefix() -> None:
    testPayload = PayloadForTesting()

    cb = Callback(testPayload.secret)
    json = cb.verify(testPayload.payload, testPayload.header)
    assert json["test"] == 2432232314

    cb = Callback("cbsec_" + testPayload.secret)

    json = cb.verify(testPayload.payload, testPayload.header)
    assert json["test"] == 2432232314


def test_sign_function() -> None:
    key = "cbsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"
    evt_id = "msg_p5jXN8AQM9LWM0D4loKWxJek"
    timestamp = datetime.fromtimestamp(1614265330, tz=timezone.utc)
    payload = '{"test": 2432232314}'
    expected = "v1,g0hM9SsE+OTPJTGt/tmIKtSyZlE3uFJELVlNIOLJ1OE="

    cb = Callback(key)
    signature = cb.sign(evt_id=evt_id, timestamp=timestamp, data=payload)
    assert signature == expected
