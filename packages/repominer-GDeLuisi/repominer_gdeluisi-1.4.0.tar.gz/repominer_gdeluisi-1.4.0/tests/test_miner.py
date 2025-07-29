from repository_miner.git import *
from repository_miner import RepoMiner
from repository_miner import execute_command,cmd_builder
from pytest import fixture,mark,param
from pathlib import Path
from subprocess import check_output
from repository_miner.data_typing import *
from concurrent.futures import ProcessPoolExecutor
from json import detect_encoding
import re
from pytest import raises
main_path=Path.cwd()
test_path=main_path.parent.joinpath("pandas")
@fixture
def git():
    return RepoMiner(main_path.as_posix())

def test_log(git):
    res=git.retrieve_commits(merges=True)
    t=check_output(f"git -C {main_path.as_posix()} log --pretty=format:%H",text=True,shell=True).splitlines()
    for i,c in enumerate(res):
        print(c.commit_hash,t[i])
        assert c.commit_hash == t[i]
    
def test_count(git):
    res=git.n_commits()
    t=int(execute_command(cmd_builder("rev-list",main_path.as_posix(),"HEAD","--count")))
    assert t==res
    
def test_local_branches(git):
    res=check_output(f"git -C {main_path.as_posix()} branch -l",text=True,shell=True).split("\n")[:-1]
    res=list(map(lambda a: a.strip("*").strip(),res))
    heads=list(git.local_branches())
    res_hashes=[]
    for hashes in map(lambda a: execute_command(cmd_builder("rev-parse",main_path.as_posix(),a)),res):
        res_hashes.append(hashes)
    assert len(res)==len(heads)
    assert set(res)==set(map(lambda h:h.name,heads))
    assert set(res_hashes)==set(map(lambda h:h.hash,heads))
    for head in heads:
        res=len(check_output(f"git -C {main_path.as_posix()} log {head.name} --pretty=\"format:%h\"",text=True,shell=True).splitlines())
        assert res==len(list(head.traverse_commits()))

def test_tree(git):
    tree = git.tree("HEAD")
    t=check_output(f"git -C {main_path.as_posix()} ls-tree HEAD -r -t --format=\"%(objectname)\" ",text=True,shell=True).split("\n")[:-1]
    t.sort()
    traverse=list(tree.traverse())
    traverse.sort(key=lambda a:a.hash)
    t_hash=[i.hash for i in traverse]
    assert t_hash  == t
    with raises(ValueError):
        tree=git.tree("askjbdkasdba")
        
def test_author(git):
    print(git.authors())
    
def test_get_commit(git):
    print(git.get_commit("HEAD"))
    with raises(GitCmdError):
        git.get_commit("asjhdbjashgdjhgas")
    
def test_get_source(git):
    blobs= [i for i in git.iterate_tree("HEAD",True) if isinstance(i,Blob)]
    for b in blobs:
        by=check_output(f"git -C {main_path.as_posix()} cat-file -p {b.hash}",shell=True).strip()
        assert b.get_source() == re.split(r"\r\n|\r|\n",by.decode(encoding=detect_encoding(by)))
        
def test_pickle_compatibility(git):
    with ProcessPoolExecutor() as exec:
        commmits=exec.submit(git.retrieve_commit_list)
        heads=exec.submit(git.local_branches_list)
        items=exec.submit(git.resolve_tree,"HEAD")
    assert commmits.result()==list(git.retrieve_commits())
    assert heads.result()==list(git.local_branches())
    assert items.result()==list(git.iterate_tree("HEAD"))

def test_get_tags(git):
    res=check_output(f"git -C {main_path.as_posix()} tag -l",text=True,shell=True).strip()
    res_tags=res.split("\n")
    tags=list(git.get_tags())
    for r,t in zip(res_tags,tags):
        assert r==t.name
        assert git.get_commit(t.hash).subject==check_output(f"git -C {main_path.as_posix()} log {r} -1 --pretty=%s",text=True,shell=True).strip()

@mark.parametrize("name,expected",
                [param(None,None,marks=mark.xfail),
                param("1.1.0","72864113e4b38c572947482e88b2650a36dd715a"),
                param("2.0.0",None,marks=mark.xfail),
                ])
def test_get_tag(git,name,expected):
    tag=git.get_tag(name)
    tag.hash==expected

@mark.parametrize("name,expected",
                [param(None,None,marks=mark.xfail),
                param("development","a01c2aa2d056f8b18853a346d13289f37f2fe96b"),
                param("not",None,marks=mark.xfail),
                ])
def test_get_branch(git,name,expected):
    tag=git.get_branch(name)
    tag.hash==expected
