#!/usr/bin/python

# pip3 install pyyaml
# import configparser
import os
import shutil
import yaml
import re
import sys
import argparse
from dateutil.parser import parse as dateparse
import subprocess

class MyTagger:
    def __init__(self):
        #self.config = ConfigParser.RawConfigParser()
        self.config = self.loadYaml("config.yml")
        self.repos = self.config['repositories']
        self.release = self.config['release-repo']
        self.workdir = "/tmp/tagger"
        self.parser = self.getParser()

    def parseDate(self, date):
        return dateparse(date).strftime("%Y-%m-%d")

    def getParser(self):
        parser = argparse.ArgumentParser(prog='tagger.py')
        subparsers=parser.add_subparsers()
        sp_sprint=subparsers.add_parser('sprint')
        sp_sprint.add_argument('num', nargs=1, type=int)
        sp_sprint.add_argument('--as-of-date', nargs=1, type=self.parseDate)
        sp_sprint.add_argument('--since', nargs=1)
        sp_sprint.set_defaults(action=self.tagSprint)

        sp_deploy=subparsers.add_parser('deploy')
        sp_deploy.add_argument('--deploy-date', nargs=1, type=self.parseDate)
        sp_deploy.add_argument('--since', nargs=1)
        sp_deploy.set_defaults(action=self.tagDeploy)

        sp_report=subparsers.add_parser('report')
        sp_report.add_argument('--since', nargs=1, required=True)
        sp_report.add_argument('--until', nargs=1, default="master")
        sp_report.set_defaults(action=self.tagReport)
        return parser

    def parse(self):
        return self.parser.parse_args()

    def loadYaml(self, f):
        with open(f, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit("Yaml load error")

    def initDir(self):
        try:
            shutil.rmtree(self.workdir, ignore_errors=True)
            print(self.workdir + " removed")
        except Exception as e:
            print(e)
        try:
            os.makedirs(self.workdir)
            print(self.workdir + " created")
            os.chdir(self.workdir)
            self.clone(self.release)
        except Exception as e:
            print(e)
            exit("Could not prepare work dir: {}".format(self.workdir))

    def getArgv(self, argindex, defval):
        if len(sys.argv) > argindex:
            return sys.argv[argindex]
        return defval

    def dir(self, dir):
        print("cd {}".format(dir))
        os.chdir(dir)

    def clone(self, repo):
        try:
            self.dir(self.workdir)
            self.oscall("git clone " + repo, redirect=True)
        except Exception as e:
            print(e)
            exit("Could not clone {}".format(repo))

    def oscall(self, command, redirect=False):
        print(command)
        if (redirect):
            command += " >> clone.txt 2>&1"
        os.system(command)

    def getCommit(self, date):
        if (date == None):
            res = subprocess.run(
                [
                    "git",
                    "rev-list",
                    "-1",
                    "master"
                ],
                capture_output=True
            )
            return res.stdout.decode("utf-8").strip('\n')
        else:
            res = subprocess.run(
                [
                    "git",
                    "rev-list",
                    "-1",
                    "--before",
                    date,
                    "master"
                ],
                capture_output=True
            )
            return res.stdout.decode("utf-8").strip('\n')

    def tag(self, repo, tag, date):
        try:
            name = self.getRepoName(repo)
            print("Tagging {} with {}".format(name, tag))
            self.dir(self.getCloneDir(repo))
            commit = self.getCommit(date)
            print(commit)
            if (commit != ""):
                self.oscall("git tag {} {}".format(tag, commit))
                self.oscall("git push origin {}".format(tag))
        except Exception as e:
            print(e)
            exit("Could not tag: {} with {}".format(repo, tag))

    def getRepoName(self, repo):
        m=re.search(r'/([^/]+)\.git\s*$', repo)
        return m.group(1)

    def getCloneDir(self, repo):
        return '{}/{}'.format(self.workdir, self.getRepoName(repo))

    def cloneRepos(self):
        for repo in self.repos:
            self.clone(repo)

    def tagSprint(self, args):
        tag='sprint-{}'.format(args.num[0])
        date=args.as_of_date[0] if args.as_of_date else None
        for repo in self.repos:
            self.tag(repo, tag, date)

    def tagDeploy(self):
        print('deploy')

    def tagReport(self, args):
        rpt = "{}/report.md".format(self.workdir)
        self.oscall("echo '# Release Report' > {}".format(rpt))
        for repo in self.repos:
            self.dir(self.getCloneDir(repo))
            self.oscall("echo '## {}' >> {}".format(self.getRepoName(repo), rpt))
            since=args.since[0]
            until=args.until
            self.oscall("git log --date=short --format='- %h %ad %s' {}..{} >> {}".format(since,until,rpt))
        self.oscall("cat {}".format(rpt))

myTagger = MyTagger()
args = myTagger.parse()
myTagger.initDir()
myTagger.cloneRepos()
args.action(args)
