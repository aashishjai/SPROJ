HTTP/1.1 302 Found
Cache-Control: no-cache,no-store,max-age=0,must-revalidate
Connection: Close
Content-Length: 0
Date: Fri, 21 Aug 2020 19:20:15 GMT
Expires: Fri, 21 Aug 2020 19:20:16 GMT
Last-Modified: Fri, 21 Aug 2020 19:20:16 GMT
Location: https://yandex.com/
NEL: {"report_to": "network-errors", "max_age": 86400, "success_fraction": 0.001, "failure_fraction": 0.1}
P3P: policyref="/w3c/p3p.xml", CP="NON DSP ADM DEV PSD IVDo OUR IND STP PHY PRE NAV UNI"
Report-To: { "group": "network-errors", "max_age": 86400, "endpoints": [ { "url": "https://dr.yandex.net/nel"}]}
Set-Cookie: yandexuid=8818146991598037615; Expires=Mon, 19-Aug-2030 19:20:15 GMT; Domain=.yandex.com; Path=/
X-Content-Type-Options: nosniff

