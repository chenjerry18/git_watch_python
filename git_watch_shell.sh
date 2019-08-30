!/bin/bash

git_remote=$1 #git repository path like https://github.com/chenjerry18/git_watch_python.git
branch=$2 # branch name
pk_path=$3 # public key (deploy key) path
script_name=$4 # script to run
submit_by=$5 # who submits this job
working_dir=$6 # the working directory

date_fmt="+%Y-%m-%d %H:%M:%S"
commitmsg="user $submit_by auto-commit"
formatted_commitmsg="$(sed "s/%d/$(date "$date_fmt")/" <<< "$commitmsg")"
regex='\/([A-Za-z_]*)\.git'
pushd $working_dir
tempdir=$(mktemp -d temp.XXXX)
pushd $tempdir
[[ $git_remote =~ $regex ]] && dir_name=${BASH_REMATCH[1]} # get the directory name from the git remote path
# make git use the deploy key
export GIT_SSH_COMMAND="ssh -i $pk_path"
# check if we are on a detached HEAD
headref=$(git symbolic-ref HEAD 2> /dev/null)
if [ $? -eq 0 ]; then
push_cmd="git push $git_remote $(sed "s_^refs/heads/__" <<< "$headref"):$branch"
else
push_cmd="git push $git_remote $branch"
fi
clone_cmd="git clone --single-branch --branch $branch $git_remote"
eval $clone_cmd
pushd $dir_name
sh $script_name
status=$(git status -s)
# commit only when status shows tracked changes.
if [ -n "$status" ]; then
git add --all
git commit -m "$formatted_commitmsg"
eval $push_cmd
fi
popd
rm -rf $dir_name
popd
rm -r $tempdir
