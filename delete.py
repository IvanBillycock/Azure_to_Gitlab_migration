
# -*- coding: utf-8 -*-
import requests
import os

requests.packages.urllib3.disable_warnings() 

gitlab_project = '35'
gitlab_server = "10.130.5.194"
gitlab_token = "gvpNcPSVzxnzTYfoeBnv"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

filepath = os.path.join(ROOT_DIR, 'deleteitems.txt')

gitlab_headers = {
    'PRIVATE-TOKEN': '{0}'.format(gitlab_token)
    }

with open(filepath) as fp:
    line = fp.readline()
    for line in fp:
        azure_id = line.replace('\n', '')
        issue_url = 'https://{0}/api/v4/projects/{1}/issues/{2}'.format(gitlab_server, gitlab_project, azure_id)
        requests.delete(issue_url, headers=gitlab_headers, verify=False)
        print("..........................." + azure_id + "...........................")
fp.close()