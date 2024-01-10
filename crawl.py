import requests
from PyDriller import Repository

def url_crawl (url):
    res = requests.get('https://api.github.com/repos/{}'.format(url))
    if repo_res.status_code == 200:
        return res.json()
    else:
        return {}

def repo_crawl (user, repo):
    url = '{}/{}'.format(user, repo)
    return url_crawl(url)

def commits_crawl (user, repo):
    url = '{}/{}/commits'.format(user, repo)
    return url_crawl(url)

