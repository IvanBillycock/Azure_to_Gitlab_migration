# -*- coding: utf-8 -*-
import requests
import os
import json
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings() 

gitlab_project = '35'
gitlab_server = "10.130.5.194"
gitlab_token = "gvpNcPSVzxnzTYfoeBnv"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

filepath = os.path.join(ROOT_DIR, 'workitems.txt')
error_path = os.path.join(ROOT_DIR, 'error.txt')
userlist_path = os.path.join(ROOT_DIR, 'userlist.csv')
folder = os.path.join(ROOT_DIR, 'issues')
if not os.path.exists(folder):
    os.makedirs(folder)


azure_headers = {
    'Authorization': 'Basic OjNqZmtpMnNxaG5ybmpiNDdvcTJrNWZ5NmtndGFscDdjZnB5anVrczVzM55yYXYzdnB5cnE='
    }
gitlab_headers = {
    'PRIVATE-TOKEN': '{0}'.format(gitlab_token)
    }
gitlab_post_issue_headers = {
    'PRIVATE-TOKEN': '{0}'.format(gitlab_token),
    'Content-Type': 'application/json'
    }

gitlab_upload_url = 'https://{0}/api/v4/projects/{1}/uploads'.format(gitlab_server, gitlab_project)
gitlab_post_issue_url = 'https://{0}/api/v4/projects/{1}/issues'.format(gitlab_server, gitlab_project)
gitlab_labels_url = 'https://{0}/api/v4/projects/{1}/labels'.format(gitlab_server, gitlab_project)

def create_label(self): # return ID
    payload = json.dumps({
    "name": "{0}".format(self),
    "color": "#f0ffff"
        })
    json.loads(requests.post(gitlab_labels_url, headers=gitlab_post_issue_headers, data=payload, verify=False).text)

def get_gitlab_user_id(self):
    azure_name = self.split("\\")[-1]
    user_dict = dict()
    userlist = open(userlist_path)
    for line in userlist:
        line = line.strip('\n')
        (key, val) = line.split(";")
        user_dict[key] = val

    for key, value in user_dict.items():
        if value == azure_name:
            return key
            userlist.close()
    return 2
    userlist.close()

def get_images(self, itemID):
    img_links = ''
    soup = BeautifulSoup(self, 'lxml')
    image_count = int("1")
    for child in soup.recursiveChildGenerator():
        if (child.name == "img"):
            ### Get
            image_url = (child['src']).replace('\\', '').replace('"', "")
            image_name = 'image_{0}.png'.format(image_count)
            image_request = requests.get(image_url, headers=azure_headers, verify=False)
            file = '{0}\{1}'.format(folder, image_name)
            open(file, 'wb').write(image_request.content)
            ### Upload
            files = {'file': open(file, 'rb')}
            img_response = json.loads(requests.post(gitlab_upload_url, headers=gitlab_headers, files=files, verify=False).text)
            get_img_link = (json.dumps(img_response['markdown'], ensure_ascii=False)).replace('\"', '')
            img_links = img_links + ("{0}<br>".format(get_img_link))
            image_count  += 1
        else:
            pass
    return img_links + self.replace('\"', '')

def create_issue(itemID):

    """Main Azure Response"""
    azure_response = json.loads(requests.get(azure_url, headers=azure_headers, verify=False).text)
    status_azure = (json.dumps(azure_response['fields']['System.State'], ensure_ascii=False).replace('\"', ''))

    try:
        issue_title = (json.dumps(azure_response['fields']['System.Title'], ensure_ascii=False).replace('\"', ''))
    except:
        with open(error_path, 'a') as error_file:
            error_file.write("{0}\n".format(itemID))
            error_file.close()
            return

    """Get and Upload body images"""
    try:
        body_xml = json.dumps(azure_response['fields']['System.Description'], ensure_ascii=False)
    except:
        body_xml = ''
    main_body = get_images(body_xml, itemID)

    """Get and Upload Attachments"""
    attach_count = int("1")
    attach_list = ''
    try:
        while json.dumps(azure_response['relations'][attach_count]['rel'], ensure_ascii=False):
            rel = (json.dumps(azure_response['relations'][attach_count]['rel'], ensure_ascii=False)).replace('\"', '')
            if rel == "AttachedFile":
                ### Get
                attach_url = (json.dumps(azure_response['relations'][attach_count]['url'], ensure_ascii=False)).replace('\"', '')
                attach_name = (json.dumps(azure_response['relations'][attach_count]['attributes']['name'], ensure_ascii=False)).replace('\"', '')
                attach_request = requests.get(attach_url, headers=azure_headers, verify=False)
                file = '{0}\{1}'.format(folder, attach_name)
                open(file, 'wb').write(attach_request.content)
                ### Upload
                attach_files = {'file': open(file, 'rb')}
                attach_response = json.loads((requests.post(gitlab_upload_url, headers=gitlab_headers, files=attach_files, verify=False)).text)
                attach_link = (json.dumps(attach_response['markdown'], ensure_ascii=False)).replace('\"', '')
                attach_list = attach_list + ("{0}<br>".format(attach_link))
                attach_count += 1
            else:
                attach_count += 1
                pass
    except:
        pass

    try:
        get_created_by = json.dumps(azure_response['fields']['System.CreatedBy']['displayName'], ensure_ascii=False).replace('\"', '')
    except:
        get_created_by = ''
    created_by = '<div><b>Created By:</b> {0}</div>'.format(get_created_by)
    try:
        get_AssignedTo = json.dumps(azure_response['fields']['System.AssignedTo']['uniqueName'], ensure_ascii=False).replace('\"', '')
        gitlab_user_id = get_gitlab_user_id(get_AssignedTo)
    except:
        gitlab_user_id = 2

    try:
        get_iteration_label = json.dumps(azure_response['fields']['System.IterationPath'], ensure_ascii=False).replace('\"', '')
    except:
        get_iteration_label = "Iteration"
    get_iteration_label = (get_iteration_label.split('\\', 1)[-1]).replace('\\', ' ')
    iteration_label = 'Итерация:{0}'.format(get_iteration_label)
    create_label(iteration_label)
    
    try:
        get_area_label = json.dumps(azure_response['fields']['System.AreaPath'], ensure_ascii=False).replace('\"', '')
    except:
        get_area_label = "Area"
    get_area_label = (get_area_label.split('\\', 1)[-1]).replace('\\', ' ')
    area_label = 'Область:{0}'.format(get_area_label)
    create_label(area_label)

    if status_azure == "Активно":
        status_label = 'Активно'
    elif status_azure == "Предложено":
        status_label = 'Предложено'
    else:
        status_label = ""
    create_label(status_label)

    try:
        get_azure_type = json.dumps(azure_response['fields']['System.WorkItemType'], ensure_ascii=False).replace('\"', '')
    except:
        get_azure_type = "Задача"    

    if get_azure_type == "Ошибка":
        issue_type = "incident"
    else:
        issue_type = "issue"

    rel_count = int("0")
    try:
        while json.dumps(azure_response['relations'][rel_count]['rel'], ensure_ascii=False):
            rel_name = (json.dumps(azure_response['relations'][rel_count]['attributes']['name'], ensure_ascii=False)).replace('\"', '')
            if rel_name == "Родительское":
                parent_url = (json.dumps(azure_response['relations'][rel_count]['url'], ensure_ascii=False)).replace('\"', '')
                rel_count += 1
            else:
                rel_count += 1
                pass
    except:
        pass

    if "parent_url" in locals():
        parent_id = parent_url.split('/')[-1]
        post_parent_url = 'https://dis-dev-ops.ics.perm.ru/Common/CouncilOfArchitects/_apis/wit/workitems/{0}?api-version=5.0&$expand=Relations'.format(parent_id)
        parent_response = json.loads(requests.get(post_parent_url, headers=azure_headers, verify=False).text)
        try:
            parent_title = (json.dumps(parent_response['fields']['System.Title'], ensure_ascii=False).replace('\"', ''))
        except:
            parent_title = "-"
        parent_title = '<div><b>Parent Title:</b> {0}</div>'.format(parent_title)
    else:
        parent_title = "-"
        parent_title = '<div><b>Parent Title:</b> {0}</div>'.format(parent_title)

    main_body = parent_title + created_by + attach_list + main_body

    payload = json.dumps({
        "title": "{0}".format(issue_title),
        "issue_type": "{0}".format(issue_type),
        "labels": "{0}, {1}, {2}".format(area_label, iteration_label, status_label),
        "iid": "{0}".format(itemID),
        "assignee_id": "{0}".format(gitlab_user_id),
        "description": "{0}".format(main_body)
        })

    """POST issue"""
    json.loads(requests.post(gitlab_post_issue_url, headers=gitlab_post_issue_headers, data=payload, verify=False).text)

    """PUT Close event"""
    if status_azure == "Закрыто":
        put_close_issue_url = "https://{0}/api/v4/projects/{1}/issues/{2}?state_event=close".format(gitlab_server, gitlab_project, itemID)
        requests.put(put_close_issue_url, headers=gitlab_headers, verify=False)
    else:
        pass

    """Get and POST comments"""
    post_commet_url = "https://{0}/api/v4/projects/{1}/issues/{2}/discussions".format(gitlab_server, gitlab_project, itemID)

    comments_response = json.loads((requests.get(get_comments_url, headers=azure_headers, verify=False)).text)

    comments_count = 0
    try:
        while json.dumps(comments_response['comments'][comments_count]['text'], ensure_ascii=False):
            comment_body = json.dumps(comments_response['comments'][comments_count]['text'], ensure_ascii=False)
            comment_body_plus = get_images(comment_body, itemID)
            autor = json.dumps(comments_response['comments'][comments_count]['revisedBy']['displayName'], ensure_ascii=False).replace('\"', '')
            if autor == "TFSBuild":
                comments_count += 1
                pass
            else:
                created_by_comment = '<div><b>Created By:</b> {0}</div>'.format(autor)
                comment_body_full = created_by_comment + comment_body_plus
                payload = json.dumps({
                    "body": "{0}".format(comment_body_full)
                    })
                json.loads(requests.post(post_commet_url, headers=gitlab_post_issue_headers, data=payload, verify=False).text)
                comments_count += 1
    except :
        pass

with open(filepath) as fp:
    line = fp.readline()
    for line in fp:
        azure_id = line.replace('\n', '')
        azure_url = 'https://dis-dev-ops.ics.perm.ru/Common/CouncilOfArchitects/_apis/wit/workitems/{0}?api-version=5.0&$expand=Relations'.format(azure_id)
        get_comments_url = "https://dis-dev-ops.ics.perm.ru/Common/CouncilOfArchitects/_apis/wit/workitems/{0}/comments?api-version=5.0-preview.2".format(azure_id)
        print("..........................." + azure_id + "...........................")
        check_url = 'https://{0}/api/v4/projects/{1}/issues?iids[]={2}'.format(gitlab_server, gitlab_project, azure_id)
        check_issue_response = json.loads((requests.get(check_url, headers=gitlab_headers, verify=False)).text)
        if not check_issue_response:
            print("Create the issue")
            create_issue(azure_id)
        else:
            print("Issue exists")
fp.close()
