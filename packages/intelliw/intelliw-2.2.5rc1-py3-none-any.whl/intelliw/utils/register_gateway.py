import base64
import hashlib
import math
import os
import sys
import time
import requests

import jwt


def register_service(code, port, keepcode='false'):
    url = f"{os.environ['domain_url']}/iuap-aip-console/self/gateway/expplat/srvpath"
    data = {
        "srvid": code,
        "srvips": [f"{os.environ['local_ip']}:{port}"],
        "responseTimeout": 300000,
        "requsert"
        "keepCode": keepcode.lower() == 'true'
    }
    header = {"X-tenantId": "0"}
    sign(url, data, header)
    resp = requests.post(url=url, json=data, headers=header)
    print(resp.text)
    resp.raise_for_status()


def sign(url: str, params: dict, headers: dict):
    params['AuthSdkServer'] = "true"
    headers['YYCtoken'] = sign_authsdk(url, params)
    return headers, params


def sign_authsdk(url: str, params: dict, ak=None, ase=None) -> str:
    """
    generate iuap signature

    :param url: request url, without parameters
    :param params:  request parameters, x-www-form-urlencoded request's body parameters should also be included.
    :param ak: ACCESS KEY
    :param ase: ACCESS SECRET
    :return: iuap signature
    """
    if not ak:
        ak = os.environ['ACCESS_KEY']
    if not ase:
        ase = os.environ['ACCESS_SECRET']

    issue_at = __issue_at()
    sign_key = __build_sign_key(ak, ase, issue_at, url)
    jwt_payload = {
        "sub": url,
        "iss": ak,
        "iat": issue_at
    }
    if params is not None and len(params) > 0:
        sorted_params = sorted(params.items())
        for item in sorted_params:
            if item[1] is None:
                val = ''
            elif len(str(item[1])) >= 1024:
                val = str(__java_string_hashcode(str(item[1])))
            else:
                val = str(item[1])
            jwt_payload[item[0]] = val

    jwt_token = jwt.encode(jwt_payload, key=sign_key, algorithm='HS256')
    return jwt_token if isinstance(jwt_token, str) else jwt_token.decode('utf-8')


def __issue_at():
    issue_at = int(time.time())
    issue_at = math.floor(issue_at / 600) * 600
    return issue_at


def __build_sign_key(access_key, access_secret, access_ts, url):
    str_key = access_key + access_secret + str(access_ts * 1000) + url
    sign_key_bytes = hashlib.sha256(str_key.encode('UTF-8')).digest()
    return base64.standard_b64encode(sign_key_bytes).decode('UTF-8')


def __java_string_hashcode(s: str):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


if __name__ == '__main__':
    args = sys.argv
    # print(args)
    register_service(args[1], args[2], args[3])
