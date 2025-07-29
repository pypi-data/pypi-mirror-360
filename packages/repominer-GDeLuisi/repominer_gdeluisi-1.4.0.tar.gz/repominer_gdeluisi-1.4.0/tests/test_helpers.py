import repository_miner.helper as help
from repository_miner.utility import create_batches
from pathlib import Path
from pytest import mark,param,xfail,raises
from datetime import datetime
from subprocess import check_output
from math import ceil
main_path=Path.cwd()

@mark.parametrize("args,expected",
                [param(None,None,marks=mark.xfail),
                param(["--all"],f"git -C \"{main_path.as_posix()}\" log --all"),
                param(["--all","--no-merges"],f"git -C \"{main_path.as_posix()}\" log --all --no-merges"),
                param([],f"git -C \"{main_path.as_posix()}\" log")])
def test_cmd_builder(args,expected):
    assert help.cmd_builder("log",main_path.as_posix(),*args).strip()==expected
    

@mark.parametrize("date1,date2,expected",
                [param(datetime(2025,1,12),datetime(2024,12,12),None,marks=mark.xfail),
                param(datetime(2024,12,12),datetime(2025,1,12),["--since='2024-12-12'","--until='2025-01-12'"]),
                param(datetime(2024,12,12),None,["--since='2024-12-12'"]),
                param(None,datetime(2025,1,12),["--until='2025-01-12'"])])
def test_date_builder(date1,date2,expected):
    assert help.date_builder(date1,date2)==expected
    
@mark.parametrize("commit1,commit2,expected",
                [param(None,None,None,marks=mark.xfail),
                param(None,"development","None..development",marks=mark.xfail),
                param("main","development","development..main"),
                param("main","","main"),
                param("main",None,"main"),
                ])
def test_range_builder(commit1,commit2,expected):
    assert help.range_builder(commit1,commit2)==expected
    
@mark.parametrize("args,expected",
                [param(None,None,marks=mark.xfail),
                param(main_path.parent.as_posix(),None,marks=mark.xfail),
                param(main_path.as_posix(),check_output(f"git -C {main_path.as_posix()} rev-parse HEAD",shell=True,text=True).strip()),
                ])
def test_get_head_commit(args,expected):
    assert help.get_head_commit(args)==expected

@mark.parametrize("args,expected",
                [param(None,None,marks=mark.xfail),
                param(main_path.parent.as_posix(),False),
                param(main_path.as_posix(),True),
                ])
def test_is_repo(args,expected):
    assert help.is_dir_a_repo(args)==expected

@mark.parametrize("iterable,n,expected",[
    (list(range(150000)),10,True),
    ([],10,False),
    (list(range(150000)),0,False),
    (list(range(150000)),None,False),
    (None,10,False),
])
def test_create_batches(iterable,n,expected):
    if expected:
        tmp=list(iterable)
        n_batches=ceil(len(tmp)/n)
        batches=create_batches(iterable,n)
        assert n_batches==len(batches)
        rec_iterable=[]
        for b in batches:
            rec_iterable.extend(b)
        assert sorted(tmp)==sorted(rec_iterable)
    else:
        with raises(ValueError):
            create_batches(iterable,n)

@mark.parametrize("pretty,merges,author,follow,args,expected",[
    param(r"%ad%h",True,"GDeLuisi","tests/test_helpers.py",["--all","--numstat"],'HEAD --max-count=1 --skip=0 --pretty="format:%ad%h" --author="GDeLuisi" --all --numstat --follow -- "tests/test_helpers.py"'),
    param(r"",False,None,"",[],'HEAD --max-count=1 --skip=0 --no-merges --pretty="format:"'),
    param(None,False,None,"",[],'HEAD --max-count=1 --skip=0 --no-merges'),
])
def test_log_builder(pretty,merges,author,follow,args,expected):
    assert help.log_builder("HEAD",None,pretty,merges,1,0,author,follow,None,None,args)== expected
    with raises(ValueError) as e:
        help.log_builder("HEAD",None,pretty,merges,0,0,author,follow,None,None,args)
        help.log_builder("HEAD",None,pretty,merges,0,-1,author,follow,None,None,args)
        
@mark.parametrize("pretty,merges,author,args,expected",[
    param(r"%ad%h",True,"GDeLuisi",["--all","--numstat"],'HEAD --max-count=1 --skip=0 --pretty="format:%ad%h" --author="GDeLuisi" --all --numstat'),
    param(r"",False,None,[],'HEAD --max-count=1 --skip=0 --no-merges --pretty="format:"'),
    param(None,False,None,[],'HEAD --max-count=1 --skip=0 --no-merges'),
])
def test_rev_list_builder(pretty,merges,author,args,expected):
    assert help.rev_list_builder("HEAD",None,pretty,merges,1,0,author,None,None,args)== expected
    with raises(ValueError) as e:
        help.rev_list_builder("HEAD",None,pretty,merges,0,0,author,None,None,args)
        help.rev_list_builder("HEAD",None,pretty,merges,0,-1,author,None,None,args)
    #HEAD --max-count=1 --skip=0 --no-merges --pretty="format:%ad%h" --author="GDeLuisi" --all --numstat --follow -- "tests/test_helpers.py"