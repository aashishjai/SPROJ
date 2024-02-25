HTTP/1.1 301 Moved Permanently
Date: Fri, 21 Aug 2020 18:47:57 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 51
Connection: close
Set-Cookie: __cfduid=d1a35b1481b03d5313179d1a31aded8f11598035677; expires=Sun, 20-Sep-20 18:47:57 GMT; path=/; domain=.poki.com; HttpOnly; SameSite=Lax
Location: https://poki.com/
CF-Ray: 5c668687fabd17db-DXB
Access-Control-Allow-Origin: *
Age: 1055
Allow: HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS
Cache-Control: public, max-age=3600, stale-while-revalidate=10800, stale-if-error=86400
Vary: Accept, Accept-Encoding
Via: 1.1 google
CF-Cache-Status: HIT
access-control-allow-headers: authorization,origin,content-type,accept
access-control-allow-methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
cf-request-id: 04b3f268ff000017db143b0200000001
content-security-policy: frame-ancestors https://*.poki.io http://localhost:1234
document-policy: force-load-at-top
serverid: playground
x-content-type-options: nosniff
x-download-options: noopen
Server: cloudflare
alt-svc: h3-27=":443"; ma=86400, h3-28=":443"; ma=86400, h3-29=":443"; ma=86400

Moved Permanently. Redirecting to https://poki.com/