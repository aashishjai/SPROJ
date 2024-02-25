HTTP/1.1 301 Moved Permanently
Server: nginx/1.17.6
Date: Fri, 21 Aug 2020 19:16:00 GMT
Content-Type: text/html
Content-Length: 169
Connection: close
Location: https://google.com
Expires: Thu, 01 Jan 1970 00:00:01 GMT
Cache-Control: no-cache
Strict-Transport-Security: max-age=0; includeSubdomains

<html>
<head><title>301 Moved Permanently</title></head>
<body>
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx/1.17.6</center>
</body>
</html>
