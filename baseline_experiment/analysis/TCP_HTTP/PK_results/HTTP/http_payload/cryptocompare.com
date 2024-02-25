0000001
Server: cloudflare
CF-RAY: 5c66a6092973d3f3-KHI
alt-svc: h2=":443"; ma=60

HTTP/1.1 301 Moved Permanently
Date: Fri, 21 Aug 2020 19:09:28 GMT
Content-Length: 0
Connection: close
Set-Cookie: __cfduid=d0c41345115d95663f47a001c3ea7b7821598036967; expires=Sun, 20-Sep-20 19:09:27 GMT; path=/; domain=.cryptocompare.com; HttpOnly; SameSite=Lax
Location: https://www.cryptocompare.com/
CryptoCompare-VM: 1
X-Frame-Options: DENY
X-Xss-Protection: 1; mode=block
X-Content-Type-Options: nosniff
Content-Security-Policy: frame-ancestors 'self'
CF-Cache-Status: DYNAMIC
cf-request-id: 04b40619b40000d3f3e2b6220