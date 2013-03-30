import json
from pprint import pprint

with open('/home/dotcloud/environment.json') as f:
    env = json.load(f)
    # You can see this log with `dotcloud logs www`
    pprint(env)

# You should not use "/admin" user for production env.
MONGODB_SETTINGS = dict(host=env['DOTCLOUD_DATA_MONGODB_URL'] + '/admin', db='miita')

# SECRET_KEY for secure cookie.
SECRET_KEY = 'replace here with secret string'

# Your google apps domain for auth.
DOMAIN = 'example.com'
