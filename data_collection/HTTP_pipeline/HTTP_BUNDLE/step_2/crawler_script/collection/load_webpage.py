#! /usr/bin/env python3
"""To run the code, run the following in terminal:

  python3 load_webpage.py [selenium|requests] timeoutVal url [dir]

where 'selenium' makes the script run only using Selenium driver with Firefox,
      'requests' makes the script run only using requests module with modified
                 user-agent field
      'timeoutVal' is the time out value used in requests module measured in seconds (I think)
      'url' is the URL of the webpage that we'll attempt to load
      'file' is a file name for the output.  If missing, output is written to the terminal.

*** Output ***

Output will be printed to the terminal in the form of a Json record.
"""

import sys
import os
import signal
import time
import datetime
import json
import socket
from socket import gethostbyname, gaierror

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


import yourip
import encoding
import record_io

# Used for the requests driver
#LINUX_USER_AGENT = 'Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0'
LINUX_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
FIREFOX_STARTUP_TIME = 4 # seconds


def selenium_get(driver, url):
    """
    Take domain name, JSON object for the domain name, Selenium driver,
    source_IP, and populate the JSON object for the domain name according to
    the result received after sending an HTTP GET request to the domain through
    Selenium's Firefox driver.
    """
    try:
        response = driver.request('GET', url)
        enc_resp_text = encoding.encode(response.text)
        return {'response_received?': True,
                'status_code': response.status_code,
                'body': enc_resp_text,}

    except Exception as ex:
        # Expect IOErrors
        return {'response_received?': False,
                'exception_name': type(ex).__name__,
                'body': str(ex),}


class SeleniumTakingTooLongException(Exception):
    """For timing out Selenium"""


def handler(signum, frame):
    """Exception handler to raise timeout errors for Selenium."""
    raise SeleniumTakingTooLongException()


def selenium_get_time_limited(driver, url, timeout):
    """
    Take domain name, JSON object for the domain name, Selenium driver,
    source_IP, and call the selenium_get function after setting an alarm
    for timeout.
    """
    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        return selenium_get(driver, url)
    except Exception as ex:
        # Expect SeleniumTakingTooLongExceptions
        return {'response_received?': False,
                'exception_name': type(ex).__name__,
                'body': str(ex),}
    signal.alarm(0) # Cancel alarm


def firefox_get_time_limited(url, timeout, headless=True):
    from selenium import webdriver
    from seleniumrequests import Firefox

    options = webdriver.firefox.options.Options()
    if headless:
        options.set_headless(headless=True)
    driver = Firefox(options=options)
    #time.sleep(FIREFOX_STARTUP_TIME)
    result = selenium_get_time_limited(driver, url, timeout)
    driver.quit()
    return result


def get_dest_ip(response):
    ip_address = None
    try:
        if response.raw._connection.sock:
            ip_address = response.raw._connection.sock.getpeername()
        elif response.raw._fp.fp._sock:
            ip_address = response.raw._fp.fp.raw._sock.getpeername()
    except:
        ip_address = None
    return ip_address


def get_dns_ip(url):
    # Warning: This will not work for https
    url_without_scheme = url.replace('http://', '')
    url_splitted = url_without_scheme.split('/')
    domain = url_splitted[0]
    # rest = url_splitted[1:]
    # will be the empty list [] if the url_without_scheme has no slash
    # will be [''] if the url_without_scheme has a trailing slash

    try:
        return 'http://' + url_without_scheme, socket.gethostbyname(domain)
    except socket.gaierror as ge:
        if not domain.startswith('www'):
            return 'http://www.' + url_without_scheme, socket.gethostbyname('www.'+ domain)
        else:
            raise ge


def requests_get_time_limited(website_url, timeout, user_agent=LINUX_USER_AGENT):
    """Try to load a page using requests"""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        requests_session = requests.Session()
        response = requests_session.get(website_url,
                                        headers={'User-Agent': user_agent},
                                        timeout=timeout,
                                        verify=False, stream=True)
        ip_address = get_dest_ip(response)
        enc_resp_text = encoding.encode(response.text)
        print(response.status_code, website_url)
        return {'response_received?': True,
                'responded_IP': ip_address,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': enc_resp_text,}

    except Exception as ex:
    # Expect most to be sub-classes of requests.exceptions.RequestException.
        return {'response_received?': False,
                'exception_name': type(ex).__name__,
                'body': str(ex),}

def requests_ip_get_time_limited(website_url, dst_ip, timeout, user_agent=LINUX_USER_AGENT):
    """Try to load a page using requests"""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    try:
        requests_session = requests.Session()
        response = requests_session.get('http://'+ dst_ip,
                                        headers={'User-Agent': user_agent, 'Host': website_url},
                                        timeout=timeout,
                                        verify=False, stream=True, allow_redirects = True)
        ip_address = get_dest_ip(response)
        enc_resp_text = encoding.encode(response.text)
        print(response.status_code, website_url)
        return {'response_received?': True,
                'responded_IP': ip_address,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': enc_resp_text,}

    except Exception as ex:
       # Expect most to be sub-classes of requests.exceptions.RequestException.
       return {'response_received?': False,
               'exception_name': type(ex).__name__,
               'body': str(ex),}



def run_test(driver_name, timeout, original_url):
    """original_url can be a URL, as with this modules' command-line
       script, or a comment starting with #, or a pair of a URL and an IP
       address.  In the last case, it sends a GET request for that URL to
       that IP address, skipping DNS resolution.
    """
    
    if original_url.startswith('#'):
        return None
    
    start_time = datetime.datetime.now()
    source_IP = yourip.get_your_IP()
    dst_ip = ''
    
    #check if we need to call the ip address instead
    
    original_url = original_url.split()
    print(original_url) 
    if len(original_url) > 1:
        dst_ip = original_url[1]
    
    original_url = original_url[0]

    # Check whether the URL can be resolved at all
    # resolved = is_resolvable_url(dns_resolved_url)
    # if not resolved:
    #    return "resolved"

    record =  {'start_time': str(start_time),
               'source_IP': source_IP,
               'url': original_url,
               'timeout': timeout,
               'driver': driver_name,}
    
    if dst_ip:
        try:
            result = requests_ip_get_time_limited(original_url, dst_ip, timeout)
            record.update(result)
        except Exception as ex:  # the driver has had an error
            print(original_url, dns_resolved_url, str(ex))
            record['response_received?'] = False
            record['exception_name'] = type(ex).__name__
            record['body'] = str(ex)

    else:
       try:
           dns_resolved_url, dns_ip = get_dns_ip(original_url)
       except Exception as ex: # Cannot resolve the URL
           print(original_url, str(ex))
           record['dns_resolved?'] = False
           record['response_received?'] = False
           record['exception_name'] = type(ex).__name__
           record['body'] = str(ex)

       else:   # Did resolve the URL
           record['dns_resolved?'] = True
           record['effective_url'] = dns_resolved_url
           record['dns_IP'] = dns_ip

           try:
             if driver_name == "selenium":
                # There is no need to do this if Firefox and selenium 3.0 are updated
                # to the latest versions (marionette is now the default way to drive FF):
                #  https://github.com/SeleniumHQ/selenium/issues/5106
                #  https://stackoverflow.com/a/43920453
                #caps = desired_capabilities.DesiredCapabilities.FIREFOX.copy()
                #caps['marionette'] = False
                #driver = webdriver.Firefox(capabilities=caps)
                result = firefox_get_time_limited(dns_resolved_url, timeout)
                record.update(result)

             elif driver_name == "requests":
                result = requests_get_time_limited(dns_resolved_url, timeout)
                record.update(result)

             else:
                raise ValueError("Unknown driver name.")

           except Exception as ex:  # the driver has had an error
               print(original_url, dns_resolved_url, str(ex))
               record['response_received?'] = False
               record['exception_name'] = type(ex).__name__
               record['body'] = str(ex)

    end_time = datetime.datetime.now()
    record['end_time'] = str(end_time)
    return record


def main(argv):
    if len(argv) not in [4, 5]:
        print("Incorrect number of arguments in:")
        print("   ", argv)
        print("Expect 4 or 5, given", len(argv))
        print(__doc__)
        sys.exit(2)

    driver = argv[1]
    # Verifying selected driver method
    if driver not in ['requests', 'selenium']:
        print("Invalid driver selected in:")
        print("   ", argv)
        print(__doc__)
        sys.exit(2)

    timeout = int(argv[2])
    wanted_url = argv[3]

    result_dict = run_test(driver, timeout, wanted_url)
    if len(argv) == 4:
        result_str = json.dumps(result_dict, indent=4)
        print(result_str)
    else:
        out_dir_name = argv[4]
        record_io.write_record(result_dict, out_dir_name)


if __name__ == "__main__":
    main(sys.argv)
