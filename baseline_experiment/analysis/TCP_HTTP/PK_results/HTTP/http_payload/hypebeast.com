HTTP/1.1 301 Moved Permanently
Content-Type: text/html; charset=UTF-8
Server: nginx
Location: https://hypebeast.com/
Access-Control-Allow-Methods: GET,POST,PUT
Access-Control-Allow-Headers: Origin,Authorization,X-API-Version,Accept,Content-Type
X-Frame-Options: SAMEORIGIN
Access-Control-Allow-Origin: https://hypebeast.com
X-Server-ID: 24
Content-Length: 334
Accept-Ranges: bytes
Date: Fri, 21 Aug 2020 19:00:08 GMT
Via: 1.1 varnish
Age: 1059
Connection: close
X-Served-By: cache-sin18033-SIN
X-Cache: HIT
X-Cache-Hits: 2
X-Timer: S1598036408.153476,VS0,VE0
Vary: Origin, Accept, X-Requested-With, X-Forwarded-Proto

<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="refresh" content="0;url='https://hypebeast.com/'" />

        <title>Redirecting to https://hypebeast.com/</title>
    </head>
    <body>
        Redirecting to <a href="https://hypebeast.com/">https://hypebeast.com/</a>.
    </body>
</html>