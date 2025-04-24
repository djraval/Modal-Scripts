# Proxy auth tokens (beta)

To prevent users outside of your workspace from discovering and triggering web
endpoints that you create, Modal will check for two headers: `Modal-Key` and
`Modal-Secret` on HTTP requests to the endpoint. You can populate these
headers with tokens created under Settings > Proxy Auth Tokens.

By default, web endpoints created by the fastapi_endpoint, asgi_app, wsgi_app,
or web_server decorators are publicly available. The optional field
`requires_proxy_auth` protects your web endpoint by verifying a key and a
token are passed in the `Modal-Key` and `Modal-Secret` headers. Requests
without those headers will receive the HTTP error 401 Unauthorized unless
valid credentials are supplied.

    
    
    import modal
    
    @app.function()
    @modal.fastapi_endpoint(requires_proxy_auth=True)
    def app():
        return "hello world"

Copy

To trigger the endpoint, create a Proxy Auth Token, which will generate a
token ID and token secret that you use to prove the authorization of your
request. In requests to the web endpoint, add the `Modal-Key` and `Modal-
Secret` HTTP headers and supply your token in the header value.

    
    
    export TOKEN_ID=wk-1234abcd
    export TOKEN_SECRET=ws-1234abcd
    curl -H "Modal-Key: $TOKEN_ID" \
         -H "Modal-Secret: $TOKEN_SECRET" \
         https://my-secure-endpoint.modal.run

Copy

Everyone within the workspace of the web endpoint can manage the tokens that
will be accepted as valid authentication.

## Proxy-Authorization header

Previously, Modal Proxy Auth tokens used the verified the `Proxy-
Authorization` header, returning a 407 Proxy Unauthorized HTTP error in case
the token isn’t valid. We have since made an update to use `Modal-Key` and
`Modal-Secret` instead. `Proxy-Authorization` is deprecated, and users are
advised to stop using it.

The `Proxy-Authorization` header uses the `Basic` authentication scheme and
expect base64 encoding of `[TOKEN_ID]:[TOKEN_SECRET]` for the credentials. For
example:

    
    
    export TOKEN_ID=wk-1234abcd
    export TOKEN_SECRET=ws-1234abcd
    curl https://my-secure-endpoint.modal.run -H "Proxy-Authorization: Basic $(echo -n $TOKEN_ID:$TOKEN_SECRET | base64)"

Copy

