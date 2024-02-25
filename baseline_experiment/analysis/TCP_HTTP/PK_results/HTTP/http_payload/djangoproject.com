HTTP/1.1 301 Moved Permanently
Server: nginx
Content-Type: text/html
Location: https://www.djangoproject.com/
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Length: 178
Accept-Ranges: bytes
Date: Fri, 21 Aug 2020 19:03:50 GMT
Via: 1.1 varnish
Age: 0
Connection: close
X-Served-By: cache-sin18034-SIN
X-Cache: MISS
X-Cache-Hits: 0
X-Timer: S1598036629.464652,VS0,VE931

<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx</center>
</body>
</html>
