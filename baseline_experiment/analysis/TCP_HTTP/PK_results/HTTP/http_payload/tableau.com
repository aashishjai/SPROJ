HTTP/1.1 301 Moved Permanently
Content-Type: text/html
Location: https://tableau.com/
Server: nginx
X-Pantheon-Styx-Hostname: styx-fe2-a-c895cb595-6h9h2
X-Styx-Req-Id: 71185591-e3dd-11ea-9559-9a8033771baa
Cache-Control: public, max-age=86400
Content-Length: 178
Date: Fri, 21 Aug 2020 19:19:45 GMT
Connection: close
X-Served-By: cache-mdw17338-MDW, cache-sin18036-SIN
X-Cache: HIT, MISS
X-Cache-Hits: 1, 0
X-Timer: S1598037585.065268,VS0,VE202
Vary: Cookie, Cookie
Age: 2504
Accept-Ranges: bytes
Via: 1.1 varnish

<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx</center>
</body>
</html>
