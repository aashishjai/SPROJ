HTTP/1.1 301 Moved Permanently
Date: Fri, 21 Aug 2020 19:10:05 GMT
Content-Type: text/html
Content-Length: 182
Connection: close
Server: openresty/1.15.8.2
location: https://aminoapps.com/
strict-transport-security: max-age=31536000; includeSubDomains
x-envoy-upstream-service-time: 3
x-envoy-upstream-healthchecked-cluster: permalink-production.default

<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>openresty</center>
</body>
</html>
