HTTP/1.1 301 Moved Permanently
Server: Varnish
Retry-After: 0
Location: https://self.com/
Content-Length: 0
Accept-Ranges: bytes
Date: Fri, 21 Aug 2020 19:26:43 GMT
Connection: close
X-Served-By: cache-sin18048-SIN
X-Cache: HIT
X-Cache-Hits: 0
X-Timer: S1598038004.664884,VS0,VE0
Content-Security-Policy: default-src https: data: 'unsafe-inline' 'unsafe-eval'; child-src https: data: blob:; connect-src https: data: blob: wss://*.hotjar.com; font-src https: data:; img-src https: data: blob:; media-src https: data: blob:; object-src https:; script-src https: data: blob: 'unsafe-inline' 'unsafe-eval'; style-src https: 'unsafe-inline'; block-all-mixed-content; upgrade-insecure-requests
Vary: 

