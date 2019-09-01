#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
	The code for automatically push and commit to git repo
'''

import os
import argparse
import tempfile
import git
import shutil
import subprocess

ap = argparse.ArgumentParser(description="This is a tool for programmatically commit&push to GitHub.")
ap.add_argument("-g", required=True, dest="git_repo", help="required, the url for the Github repository")
ap.add_argument("-p", required=True, dest="pk", help="required, the deploy key for this repository")
ap.add_argument("-s", required=True, dest="script", help="required, the script path for updating the repository")
ap.add_argument("-b", required=True, dest="branch", help="required, the branch to update")
ap.add_argument("-d", required=True, dest="date", help="required, today's date")

args = ap.parse_args()

commitmsg = "Submitted on {} by auto-commit".format(args.date)

ssh_cmd = "ssh -i {}".format(args.pk)

with tempfile.TemporaryDirectory(dir=os.getcwd()) as tmp:
	with git.Repo.clone_from(args.git_repo, tmp, branch=args.branch, env=dict(GIT_SSH_COMMAND=ssh_cmd)) as repo:
		
		diff = repo.index.diff(None)
		if len(diff) == 0:
			raise Exception("There are no changes to submit")
		print("File changes:")
		for item in diff:
			print(item.a_path)
		repo.git.add(u=True) # only submit modification changes
		repo.index.commit(commitmsg)
		origin = repo.remote(name="origin")
		origin.push()
