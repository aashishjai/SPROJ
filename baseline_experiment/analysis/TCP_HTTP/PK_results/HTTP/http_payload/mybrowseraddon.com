
alt-svc: h2=":443"; ma=60

eb
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>301 Moved Permanently</title>
</head><body>
<h1>Moved Permanently</h1>
<p>The document has moved <a href="https://mybrowseraddon.com/">here</a>.</p>
</body></html>

HTTP/1.1 301 Moved Permanently
Date: Fri, 21 Aug 2020 19:12:31 GMT
Content-Type: text/html; charset=iso-8859-1
Transfer-Encoding: chunked
Connection: close
Set-Cookie: __cfduid=d7ce9a3231733ae178936f17fd6ca54ae1598037150; expires=Sun, 20-Sep-20 19:12:30 GMT; path=/; domain=.mybrowseraddon.com; HttpOnly; SameSite=Lax
Location: https://mybrowseraddon.com/
Cache-Control: max-age=14400
CF-Cache-Status: MISS
cf-request-id: 04b408e3920000d3fb1d887200000001
Vary: Accept-Encoding
Server: cloudflare
CF-RAY: 5c66aa7f58b9d3fb-KHI0

HTTP/1.1 301 Moved Permanently
Date: Fri, 21 Aug 2020 19:12:31 GMT
Content-Type: text/html; charset=iso-8859-1
Transfer-Encoding: chunked
Connection: close
Set-Cookie: __cfduid=d7ce9a3231733ae178936f17fd6ca54ae1598037150; expires=Sun, 20-Sep-20 19:12:30 GMT; path=/; domain=.mybrowseraddon.com; HttpOnly; SameSite=Lax
Location: https://mybrowseraddon.com/
Cache-Control: max-age=14400
CF-Cache-Status: MISS
cf-request-id: 04b408e3920000d3fb1d887200000001
Vary: Accept-Encoding
Server: cloudflare
CF-RAY: 5c66aa7f58b9d3fb-KHI