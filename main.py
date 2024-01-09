import os, sys
import requests
import json
import datetime
from pydriller import Repository
from git import Repo


url = 'https://github.com/Grizzlazy/q_coverage'

def get_last_char (path, ch):
    loc1 = path.rfind(ch)
    name = path[loc1+1: len(path)]
    return loc1, name

loc, extend = get_last_char(url, '.')
if extend == 'git':
    url = url[1: loc]

loc, repo = get_last_char(url, '/')
loc, owner = get_last_char(url[1: loc], '/')


#raw
repo_url = f'https://api.github.com/repos/{owner}/{repo}'
raw = {}

#lang + domain + owner
respond = requests.get(repo_url)
if respond.status_code != 200:
    print('Cannot fetch data: ', respond.status_code)
    exit(1)
else:
    repo_res = respond.json()
    raw['language'] = repo_res['language']
    raw['domain'] = repo_res['topics']
    raw['author'] = repo_res['owner']['login']

# list contributors
respond = requests.get(repo_res['contributors_url'])
if respond.status_code != 200:
    print('Cannot fetch data: ', respond.status_code)
    exit(1)
else:
    ctb_res = respond.json()
    raw['contributors'] = []
    for contributor in ctb_res:
        raw['contributors'].append(contributor['login'])

#list issues
loc = get_last_char(repo_res['issues_url'], '{')
issues_url = repo_res['issues_url'][0: loc[0]]
#print(issues_url)
respond = requests.get(issues_url)
if respond.status_code != 200:
    print('Cannot fetch data: ', respond.status_code)
    exit(1)
else:
    issues_res = respond.json()
    raw['issues'] = []
    for issue in issues_res:
        raw['issues'].append({
            'number': issue['number'],
            'title': issue['title'],
            'user': issue['user']['login']
        })

#list commits
raw['commits'] = []
for commit in Repository(url).traverse_commits():
    if commit.lines != 0:
        raw['commits'].append({
            'sha': commit.hash,
            'committer': commit.author.name,
            'msg': commit.msg,
            'date': commit.committer_date.strftime('%xT%X'),
            'modified_files': [],
            'parents': commit.parents
        })
        for file in commit.modified_files:
            raw["commits"][-1]['modified_files'].append({
                'name': file.filename,
                'type': file.change_type.name,
                'added': file.added_lines,
                'deleted': file.deleted_lines,
                'loc': file.nloc
            })


f = open(f'{repo}_raw.json', 'w')
f.write(json.dumps(raw, indent= 4))
    

"""
ext 
"""