import os, sys
import requests
import json
import datetime
import re
from pydriller import Repository

'''
Giao diện dòng lệnh
'''
url = sys.argv[1]
#url = 'https://github.com/Mr-Duo/crawl-git'
newpath = './Data/' 
if not os.path.exists(newpath):
    os.makedirs(newpath)

def get_last_char (path, ch):
    loc1 = path.rfind(ch)
    name = path[loc1+1: len(path)]
    return loc1, name

loc, extend = get_last_char(url, '.')
if extend == 'git':
    url = url[0: loc]

loc, repo = get_last_char(url, '/')
loc, owner = get_last_char(url[1: loc], '/')


'''
crawl
'''
#raw
repo_url = f'https://api.github.com/repos/{owner}/{repo}'
raw = {}
print('Start Mining...')
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
    raw['contributors'] = []

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
contributors = set()
raw['commits'] = {}
for commit in Repository(url).traverse_commits():
    sha = commit.hash
    raw['commits'][sha] = {}
    if commit.lines != 0:
        contributors.add(commit.author.name)
        raw['commits'][sha].update({
            'author': commit.author.name,
            'msg': commit.msg,
            'date': commit.committer_date.strftime('%xT%X'),
            'added': commit.insertions,
            'parents': commit.parents,
            "deleted": commit.deletions,
            'modified_files': {}
        })
        for file in commit.modified_files:
            if file.language_supported == False:
                continue
            if file.nloc == None:
                continue
            name = file.filename
            raw['commits'][sha]['modified_files'][name] = {}
            raw["commits"][sha]['modified_files'][name].update({
                'type': file.change_type.name,
                'added': file.added_lines,
                'deleted': file.deleted_lines,
                'loc': file.nloc,
                'content': file.source_code,
                'diff': file.diff_parsed,
            })
            

        if raw['commits'][sha]['modified_files'] == {}:
            raw['commits'].popitem()
            
raw['contributors'] = list(contributors)
f = open(f'{newpath}{repo}_raw.json', 'w')
f.write(json.dumps(raw, indent= 4))
print('Mine completed!')    

"""
extract 
"""
print('Start Extracting!')
_files_ = {}

for sha, commit in raw['commits'].items():
    if len(commit.keys()) == 0:
        continue 
    dev = raw['author']
    cur_date = datetime.datetime.strptime(commit['date'], '%xT%X')

    for name, file in commit['modified_files'].items():
        if _files_.get(name) ==  None:
            _files_[name] = {}

        log = _files_[name].keys()
        NUC = set()

        if _files_[name].get(sha) == None:
            _files_[name][sha] = {
                'loc_bf': 0,
                'dev': [],
                'date': commit['date'],
                'interval': 0,
                'NUC': NUC
            }

        if len(log) > 2:
            dad = list(log)[-2]
            last_date = datetime.datetime.strptime(_files_[name][dad]['date'], '%xT%X')
            
            _files_[name][sha]['interval'] = (cur_date - last_date).total_seconds()
            _files_[name][sha]['loc_bf'] = raw['commits'][dad]['modified_files'][name]['loc']

        for s in log:
            NUC.add(s)
        NUC.discard(sha)
        
        if _files_[name][sha]['dev'].count(dev) == 0:
            _files_[name][sha]['dev'].append(dev)
 

ext = {}
pp_category = ['fix', 'patch', 'defect', 'bug', 'add']

for sha, commit in raw['commits'].items():
    if len(commit.keys()) == 0:
        continue 
    ext[sha] = {}
    ext[sha].update({
        'total_added': commit['added'],
        'total_deleted': commit['deleted'],
        'EXP': 0,
        'NUC': 0,
        'total_dev': 0,
        'avg_interval': 0,
        'modified_files': {},
        'purpose': []
    })

    for pp in pp_category:
        if commit['msg'].find(pp) != -1:
            ext[sha]['purpose'].append(pp)
    if len(ext[sha]['purpose']) == 0:
        ext[sha]['purpose'].append('other')

    AGE = 0
    NDEV = set()
    NUC = set()

    for name, file in commit['modified_files'].items():
        AGE += _files_[name][sha]['interval']
        for dev in _files_[name][sha]['dev']:
            NDEV.add(dev)

        ext[sha]['modified_files'][name] = {}
        ext[sha]['modified_files'][name].update({
            'LT': _files_[name][sha]['loc_bf'], 
            'NDEV': len(_files_[name][sha]['dev']),
        })
        NUC.update(_files_[name][sha]['NUC'])
    
    ext[sha]['avg_interval'] = AGE / len(commit['modified_files'].keys())
    ext[sha]['total_dev'] = len(NDEV)
    ext[sha]['NUC'] = len(NUC)

_exp_ = {}
for dev in raw['contributors']:
    _exp_[dev] = 0
for sha, commit in raw['commits'].items():
    if len(commit.keys()) == 0:
        continue 
    dev = commit['author']
    ext[sha]['EXP'] = _exp_[dev]
    _exp_[dev]+=1



f = open(f'{newpath}{repo}_ext.json', 'w')
f.write(json.dumps(ext, indent= 4))
print('Extract completed!')


