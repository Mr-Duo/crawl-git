from pydriller import Repository
from pydriller.metrics.process.contributors_count import ContributorsCount
url = 'https://github.com/Grizzlazy/q_coverage'

from_date = '2020-'

for commit in Repository(url).traverse_commits():
    for file in commit.modified_files:
        print(f'{file.filename} has {file.nloc} in commit {commit.hash}')
    