HTTP/1.1 301 Moved Permanently
Server: nginx/1.13.7
Date: Fri, 21 Aug 2020 19:12:49 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 148
Connection: close
Location: http://www.anandtech.com/
X-Powered-By: ASP.NET
Strict-Transport-Security: max-age=300; includeSubDomains

<head><title>Document Moved</title></head>
<body><h1>Object Moved</h1>This document may be found <a HREF="http://www.anandtech.com/">here</a></body>