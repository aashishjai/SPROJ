HTTP/1.1 301 Moved Permanently
Server: nginx
Date: Fri, 21 Aug 2020 19:14:51 GMT
Content-Type: text/html
Content-Length: 178
Connection: close
Location: http://www.yy.com/
P3P: CP=CAO PSA OUR
Access-Control-Allow-Headers: X-Requested-With
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET,POST

<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx</center>
</body>
</html>
