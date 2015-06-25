#!/usr/bin/env python                                                                    
 
"""Script to generate permenant OAuth tokens for the desired reddit scope."""
 
from __future__ import print_function
import os
import praw
import sys
from pprint import pprint
 
 
def prompt(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    return sys.stdin.readline().strip()
 
 
def main():
    if len(sys.argv) != 5:
        print('Usage: {0} CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE'
              .format(os.path.basename(sys.argv[0])))
        return 1
 
    keys = 'oauth_client_id oauth_client_secret oauth_redirect_uri'.split()
    r = praw.Reddit('reddit oauth token fetch',
                    **dict(zip(keys, sys.argv[1:5])))
 
    scope = sys.argv[-1]
    print('Requesting `{0}` scope'.format(scope))
    print('Visit: {0}'.format(r.get_authorize_url('...', scope, True)))
    pprint(r.get_access_information(prompt('Code: ')))
    return 0
 
 
if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)