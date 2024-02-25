HTTP/1.1 301 Moved Permanently
Server: nginx
Date: Fri, 21 Aug 2020 19:21:06 GMT
Content-Type: text/html
Content-Length: 162
Connection: close
Location: https://duckduckgo.com/
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: default-src https: blob: data: 'unsafe-inline' 'unsafe-eval'; frame-ancestors 'self'
X-XSS-Protection: 1;mode=block
X-Content-Type-Options: nosniff
Referrer-Policy: origin
Expect-CT: max-age=0
Expires: Sat, 21 Aug 2021 19:21:06 GMT
Cache-Control: max-age=31536000

<html>
<head><title>301 Moved Permanently</title></head>
<body>
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx</center>
</body>
</html>
