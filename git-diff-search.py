#!python
""" git-diff-search.py: Find the git commit most closely matching a given source.

This scripts requires the traits module (https://github.com/enthought/traits).

It is provided without warranty under the terms of the GNU General Public License GPLv3.

Copyright 2015 Yves Delley
"""

import os
import subprocess

import traits.api as tr

class CommitInfo(tr.HasStrictTraits):
    hash = tr.Str
    parents = tr.List(tr.This)
    children = tr.Set(tr.This)
    
    diff = tr.Either(None,tr.CLong)
    gitdiff = tr.Either(None,tr.CLong)

class MBInfo(tr.HasStrictTraits):
    """ long-distance information """
    commit = tr.Instance(CommitInfo)
    parents = tr.Dict(tr.Instance(CommitInfo),tr.This)
    children = tr.Dict(tr.Instance(CommitInfo),tr.This)  
    
class DiffStatus(tr.HasStrictTraits):
    repo = tr.Directory()
    
    src = tr.Directory()
    
    commits = tr.Dict(tr.Str,tr.Instance(CommitInfo))
    first = tr.Str(desc="hash of most recent commit")
    knots = tr.Dict(tr.Instance(CommitInfo),tr.Instance(MBInfo))
    
    @property
    def _gitargs(self):
        gp = os.path.abspath(self.repo)
        return ['git','--git-dir=%s'%os.path.join(gp,'.git'),'--work-tree=%s'%gp]
    
    def _ask_git(self,args,*a,**kw):
        try:
            ret = subprocess.check_output(
                self._gitargs+args,
                shell=False,
                *a, **kw
            )
        except subprocess.CalledProcessError as ex:
            return ex.returncode, ex.output
            print('nonzero result: ',ex.returncode,ex.cmd,ex.output)
            if ex.returncode == -1 or True:
                raise
        return 0,ret

    def _call_git(self,args,*a,**kw):
        try:
            subprocess.check_call(
                self._gitargs+args,
                shell=False,
                *a, **kw
            )    
        except subprocess.CalledProcessError as ex:
            if ex.returncode == -1:
                raise
            print('nonzero result: ',ex.returncode,ex.cmd,ex.output)
        
    def build_tree(self,*leafs):
        code,data = self._ask_git(['rev-list','--parents']+list(leafs))
        assert code>=0
        data = data.decode('ascii')
        first = None
        for line in data.split('\n'):
            if not line.strip():
                continue
            hashes = line.split()
            hash = hashes[0]
            if first is None:
                first = hash
            parents = hashes[1:]
            commit = self.commits.setdefault(hash[:7],CommitInfo(hash=hash))
            parents = [
                self.commits.setdefault(p[:7],CommitInfo(hash=p))
                for p in parents
            ]
            commit.parents = parents
            for p in parents:
                p.children.add(commit)
        self.first = first
    
    def find_net(self):
        """ Find all commits that don't have exactly one parent and one child. """
        ret = dict()
        for c in self.commits.values():
            if len(c.children) == 1 and len(c.parents) == 1:
                continue
            n = ret.setdefault(c,MBInfo(commit=c))
            for cc in c.children:
                tmp = cc
                while len(tmp.children) == 1 and len(tmp.parents) == 1:
                    tmp, = tmp.children
                nc = ret.setdefault(tmp,MBInfo(commit=tmp))
                n.children[cc] = nc
            for cp in c.parents:
                tmp = cp
                while len(tmp.children) == 1 and len(tmp.parents) == 1:
                    tmp, = tmp.parents
                np = ret.setdefault(tmp,MBInfo(commit=tmp))
                n.parents[cp] = np
        self.knots = ret
    
    def fastdiff(self,c):
        if c.diff is not None:
            return c.diff
        
        self._call_git(['checkout','-B','tmp',c.hash])
        gp = os.path.abspath(self.repo)
        sp = os.path.abspath(self.src)
        try:
            raw = subprocess.check_output(
                ['diff','-burN','-x.git',gp,sp]
            )
        except subprocess.CalledProcessError as ex:
            if ex.returncode<0:
                raise
#            print('nonzero result: ',ex.returncode,ex.cmd,ex.output[:200])
            raw = ex.output
        ret = raw.decode('utf-8','replace')
        ret = len(ret.split('\n'))
        c.diff = ret
        return ret

    def neighbouring_knots(self,commit):
        node = self.knots.get(commit,None)
        if node is None:
            # fall-back to neighbouring commits
            return self.neighbouring_commits()
        return set(node.children.values()) | set(node.parents.values())

    def neighbouring_commits(self,commit):
        return set(commit.children) | set(commit.parents)

    def follow_commits(self,node,n=100,reset=True,jump='knots',metric='fastdiff'):
        if isinstance(metric,str):
            metric = getattr(self,metric)
        if isinstance(jump,str):
            jump = getattr(self,'neighbouring_'+jump)
        seen = set()
        bestn = node
        bestv = metric(node)
        upcoming = {node:bestv}
        while upcoming and len(seen)<n:
            next = min(upcoming.values())
            for k,v in upcoming.items():
                if v == next:
                    node = k
                    break
            else:
                raise RuntimeError
            del upcoming[node]
            cur = metric(node)
            seen.add(node)
            print(
                '%7s (%9d) '%(node.hash[:7],cur),
                'best!' if cur<bestv else ''
            )
            if cur<bestv:
                bestv = cur
                bestn = node
                if reset:
                    seen = set()
                    upcoming = {}
            for new in jump(node) - seen:
                prev = upcoming.get(new,None)
                upcoming[new] = cur if prev is None else min(cur,prev)
        return bestn        

usage = """Usage:
    {0} <source> <git_repo> <head_commits>...

Finds the git commit that matches a given source tree the best.
Only commits in the ancestry of the given head commits are searched.
The search is started from the most recent commit concidered.

It will create a branch 'tmp' which will be reset to the closest commit.
"""
    
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(usage.format((list(sys.argv)+['git-diff-search'])[0]))
        sys.exit(-1)
    
    status = DiffStatus(
        src = os.path.abspath(sys.argv[1]),
        repo = os.path.abspath(sys.argv[2]),
    )
    print('=== Gathering commit tree')
    status.build_tree(*sys.argv[3:])
    print('=== Finding branching/merging commits')
    status.find_net()
    print('=== Rough search following only branch/merge commits')
    kw=dict(n=100,reset=True,metric='fastdiff')
    status.follow_commits(status.commits[status.first[:7]],jump='knots',**kw)
    print('=== Fine search following every commit')
    ret = status.follow_commits(status.commits[status.first[:7]],jump='commits',**kw)
    print('=== Finished! Best match is commit ',ret.hash)
    