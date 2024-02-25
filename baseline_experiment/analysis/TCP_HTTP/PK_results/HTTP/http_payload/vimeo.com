HTTP/1.1 301 Moved Permanently
Server: nginx
Content-Type: text/html; charset=UTF-8
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Location: https://vimeo.com/
Expires: Mon, 19 Aug 2030 19:23:29 GMT
X-BApp-Server: pweb-v2305-f52cw
Via: 1.1 varnish
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
X-Varnish-Cache: 1
X-VServer: infra-webproxy-a-16
X-Vimeo-DC: ge
Via: 1.1 varnish
Content-Length: 0
Accept-Ranges: bytes
Date: Fri, 21 Aug 2020 19:24:30 GMT
Via: 1.1 varnish
Age: 0
Connection: close
X-Served-By: cache-bwi5140-BWI, cache-sin18046-SIN
X-Cache: MISS, MISS
X-Cache-Hits: 0, 0
X-Timer: S1598037871.704476,VS0,VE240
Vary: User-Agent

