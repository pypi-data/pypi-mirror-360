# Copyright 2015, Wichert Akkerman <wichert@wiggy.net>
# Copyright 2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

import jwt
from pyramid.config import Configurator

from cubicweb_api.auth.jwt_policy import (
    JWTAuthenticationPolicy,
    JWTCookieAuthenticationPolicy,
)

log = logging.getLogger(__name__)


def create_jwt_policy(
    config: Configurator,
    prefix="cubicweb.auth.jwt",
    custom_paths: dict | None = None,
):
    cfg = config.registry.settings
    keys = (
        "private_key",
        "public_key",
        "algorithm",
        "expiration",
        "leeway",
        "http_header",
        "auth_type",
    )
    key_paths = {}
    if custom_paths is None:
        custom_paths = {}
    for k in keys:
        key_paths[k] = custom_paths.get(k, f"{prefix}.{k}")
    # private key is mandatory
    if key_paths["private_key"] not in cfg:
        raise KeyError(key_paths["private_key"])
    kwargs = {}
    for k in keys:
        if key_paths[k] in cfg:
            kwargs[k] = cfg.get(key_paths[k])
    auth_policy = JWTAuthenticationPolicy(**kwargs)
    cookie_policy = JWTCookieAuthenticationPolicy.make_from(
        auth_policy, cookie_name="CW_JWT", https_only=True, reissue_time=7200
    )
    return cookie_policy


def _request_create_token(request, principal, expiration=None, audience=None, **claims):
    return request.authentication_policy.create_token(
        principal, expiration, audience, **claims
    )


def _request_claims(request):
    try:
        return jwt.decode(
            request.cookies.get(request.authentication_policy.cookie_name),
            request.authentication_policy.private_key,
            algorithms=[request.authentication_policy.algorithm],
        )
    except Exception:
        return {}


def includeme(config: Configurator):
    log.warning("Using experimental JWT authentication. Do not use in production.")
    try:
        policy = create_jwt_policy(
            config, custom_paths={"private_key": "cubicweb.auth.authtkt.session.secret"}
        )
    except KeyError as e:
        log.warning(
            "Could not configure JWT policy: missing configuration key %s", str(e)
        )
    else:
        config.registry["cubicweb.authpolicy"]._policies.append(policy)
        config.add_request_method(_request_create_token, "create_jwt_token")
        config.add_request_method(_request_claims, "jwt_claims", reify=True)
        config.add_request_method(
            lambda request: policy, "authentication_policy", reify=True
        )
        log.info("JWT policy configured")
