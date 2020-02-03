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

class MyTagger:
    def __init__(self):
        #self.config = ConfigParser.RawConfigParser()
        self.config = self.loadYaml("config.yml")
        self.repos = self.config['repositories']
        self.release = self.config['release-repo']
        self.workdir = "/tmp/tagger"
        self.parser = self.getParser()

    def parseDate(self, date):
        return dateparse(date)

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
        sp_report.add_argument('--until', nargs=1)
        sp_report.set_defaults(action=self.tagReport)
        return parser

    def parse(self):
        args = self.parser.parse_args()
        args.action(args)

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

    def tag(self, repo, tag):
        try:
            name = self.getRepoName(repo)
            print("Tagging {} with {}".format(name, tag))
            self.dir(self.getCloneDir(repo))
            self.oscall("git tag {}".format(tag))
            self.oscall("git push origin {}".format(tag))
        except Exception as e:
            print(e)
            exit("Could not tag: {} with {}".format(repo, tag))

    def getRepoName(self, repo):
        m=re.search(r'/([^/]+)\.git\s*$', repo)
        return m.group(1)

    def getCloneDir(self, repo):
        return '{}/{}'.format(self.workdir, self.getRepoName(repo))

    def processRepos(self, tag):
        for repo in self.repos:
            self.clone(repo)
            self.tag(repo, tag)

    def tagSprint(self, args):
        print('sprint {}'.format(args.num))

    def tagDeploy(self):
        print('deploy')

    def tagReport(self):
        print('report')


myTagger = MyTagger()
myTagger.parse()

print(1)

#myTagger.initDir()
#tag = myTagger.getArgv(1, "tag")
#myTagger.processRepos(tag)
