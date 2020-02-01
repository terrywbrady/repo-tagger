#!/usr/bin/python

# pip3 install pyyaml
# import configparser
import os
import shutil
import yaml
import re
import sys

class MyTagger:
    def __init__(self):
        #self.config = ConfigParser.RawConfigParser()
        self.config = self.loadYaml("config.yml")
        self.repos = self.config['repositories']
        self.release = self.config['release-repo']
        self.workdir = "/tmp/tagger"
        self.initDir()

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

myTagger = MyTagger()
tag = myTagger.getArgv(1, "tag")
myTagger.processRepos(tag)
