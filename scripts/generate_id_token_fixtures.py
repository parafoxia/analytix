import json

from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT as JwtEncoder
from jwt import JWT as JwtDecoder
from jwt import jwk_from_dict

if __name__ == "__main__":
    key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="420")
    print("public_jwks\n-----------")
    print({"keys": [key.export_public(as_dict=True)]})

    jwt = JwtEncoder(
        header={"alg": "RS256", "typ": "JWT"},
        claims={
            "sub": "1234567890",
            "name": "Barney the Dinosaur",
            "admin": True,
            "iat": 1516239022,
        },
    )
    jwt.make_signed_token(key)
    token = jwt.serialize()
    print(f"\nid_token\n--------\n{token}")

    jwk = jwk_from_dict(json.loads(key.export_public()))
    print("\nid_token_payload\n----------------")
    print(JwtDecoder().decode(token, jwk))
