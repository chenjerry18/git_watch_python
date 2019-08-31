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

ap = argparse.ArgumentParser(description="ContentOps tool for updating schema and config files in FISS staging & devel.")
ap.add_argument("-g", required=True, dest="git_repo", help="required, the url for the Github repository")
ap.add_argument("-p", required=True, dest="pk", help="required, the deploy key for this repository")
ap.add_argument("-s", required=True, dest="script", help="required, the script path for updating the repository")
ap.add_argument("-m", required=False, dest="mgr_user", help="required, the manager account")
ap.add_argument("-d", required=True, dest="date", help="required, today's date")
ap.add_argument("-i", required=False, dest="ids", help="required, the ids file to be updated")
ap.add_argument("-b", required=False, dest="prebuild", help="optional, the prebuild directory path")
ap.add_argument("fields", type=str, help="the fields names to be updated")

args = ap.parse_args()

commitmsg = "Submitted on {} by auto-commit with manager account {}".format(args.date, args.mgr_user)

ssh_cmd = "ssh -i {}".format(args.pk)

with tempfile.TemporaryDirectory(dir=os.getcwd()) as tmp:
	with git.Repo.clone_from(args.git_repo, tmp, branch="devel", env=dict(GIT_SSH_COMMAND=ssh_cmd)) as repo:

		dest_path = os.path.join(tmp, "script.sh")
		shutil.copy(args.script, dest_path)

		failed = subprocess.call([dest_path, args.date, args.ids, args.fields, args.prebuild])
		if failed:
			raise Exception("Please check your script")

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

		git = repo.git
		git.checkout("staging")
		git.merge("devel")

		origin.push()
