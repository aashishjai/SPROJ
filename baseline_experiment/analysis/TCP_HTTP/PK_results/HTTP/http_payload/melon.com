HTTP/1.1 302 Found
Date: Fri, 21 Aug 2020 19:23:27 GMT
Server: Apache
Location: http://www.melon.com/index.htm
Content-Length: 214
Connection: close
Content-Type: text/html; charset=iso-8859-1

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>302 Found</title>
</head><body>
<h1>Found</h1>
<p>The document has moved <a href="http://www.melon.com/index.htm">here</a>.</p>
</body></html>
