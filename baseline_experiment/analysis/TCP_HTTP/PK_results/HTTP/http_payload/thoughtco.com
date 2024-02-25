HTTP/1.1 301 Moved Permanently
Server: Varnish
Retry-After: 0
Location: https://thoughtco.com/
Content-Length: 0
Accept-Ranges: bytes
Date: Fri, 21 Aug 2020 18:52:57 GMT
Via: 1.1 varnish
Connection: close
X-Served-By: cache-sin18043-SIN
X-Cache: HIT
X-Cache-Hits: 0
X-Timer: S1598035978.665139,VS0,VE0
NEL: {"report_to":"network-errors","max_age":2592000,"success_fraction":0,"failure_fraction":1.0, "include_subdomains": true}
Report-To: {"group":"network-errors","max_age":2592000,"endpoints":[{"url":"https://r.3gl.net/hawklogserver/561/re.p"}]}

