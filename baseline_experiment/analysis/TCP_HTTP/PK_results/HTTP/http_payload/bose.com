HTTP/1.1 302 Moved Temporarily
Content-Length: 0
Connection: close
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Origin: *
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Date: Fri, 21 Aug 2020 19:02:16 GMT
Expires: 0
Location: https://www.bose.com
Nebula-Response-Details: reason: Exact match; rule-id: 1e483dd8-c4d8-4468-b904-2257beaeef98
nebula_service: pulsar
Pragma: no-cache
Server: nginx/1.14.2
X-Application-Context: pulsar:prod02:9070
X-B3-Sampled: 1
X-B3-SpanId: 4d7205c5326e9597
X-B3-TraceId: 4d7205c5326e9597
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
X-Cache: Miss from cloudfront
Via: 1.1 775834d9413c7c2b7eb733af43d3132f.cloudfront.net (CloudFront)
X-Amz-Cf-Pop: FJR50-C1
X-Amz-Cf-Id: rR4zmPqkW_IlEKTgXfybo57ILkH_bBJUQMU_XuGwNhP3lM93x0Jr2g==

