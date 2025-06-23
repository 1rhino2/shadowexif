git filter-branch -f --env-filter '
export GIT_AUTHOR_NAME="1rhino2"
export GIT_AUTHOR_EMAIL="xmansussy@yahoo.com"
export GIT_COMMITTER_NAME="1rhino2"
export GIT_COMMITTER_EMAIL="xmansussy@yahoo.com"
' --tag-name-filter cat -- --branches --tags
