#!/usr/bin/env python3
import praw
from userinfo import reddit

r = praw.Reddit(user_agent=reddit['useragent'])
r.set_oauth_app_info(client_id=reddit['client_id'],
    client_secret=reddit['client_secret'],
    redirect_uri=reddit['redirect_uri'])
r.refresh_access_information(reddit['refresh_key'])

authenticated_user = r.get_me()
print authenticated_user.name, authenticated_user.link_karma