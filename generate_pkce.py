
import hashlib
import secrets
import base64

code_verifier = secrets.token_urlsafe(64)

code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode("ascii")).digest()
).rstrip(b"=").decode("ascii")

print("CODE_VERIFIER:", code_verifier)
print("CODE_CHALLENGE:", code_challenge)
