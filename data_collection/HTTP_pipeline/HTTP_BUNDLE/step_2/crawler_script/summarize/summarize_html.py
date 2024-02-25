#! /usr/bin/env python3

"""Replace HTML body with summary of what was there

Call with python summarize_html.py <record_dir> <out_dir>
"""

import sys
import os
import errno

import record_io
import categorize


def summarize(records_dir_name, out_dir_name):
    """Summarize the records in records_dir_name"""
    records = record_io.read_directory(records_dir_name)
    for url_key in records:
        url_record = records[url_key]

        # We only need to summarize the HTML, which only exists if
        # a resonse was received.
        if url_record['response_received?']:
            # If a response is received, we know there's a status
            # code and a body.  (There's also headers and a
            # dest. IP, but we don't need those.)
            status = url_record['status_code']
            headers = url_record['headers']
            body = url_record['body']
            # Since the body is huge, remove it and put in the
            # category and body length instead:
            abnormal, why = categorize.response(status, headers, body)
            del url_record['body']
            url_record['block_page?'] = abnormal
            url_record['category'] = why
            url_record['body_length'] = len(body)
    record_io.write_directory(records, out_dir_name)


if __name__== '__main__':

    if len(sys.argv) != 3:
        print('Not the right number of enough arguments. You gave: ')
        print(sys.argv)
        print("Instructions:")
        print(__doc__)
        sys.exit(2)

    results_dir_name = sys.argv[1]
    out_dir_name = sys.argv[2]
    summarize(results_dir_name, out_dir_name)
