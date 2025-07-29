from repository_miner.git import *
from pytest import fixture,mark,param
from pathlib import Path
from repository_miner import execute_command,cmd_builder
main_path=Path.cwd()
@fixture
def git():
    return Git(main_path.as_posix())

@mark.parametrize("args,expected",[
    param("rev_parse",execute_command(cmd_builder("rev-parse",main_path.as_posix(),"HEAD")).strip()),
    param("rev_pars",None,marks=mark.xfail),
    param("",None,marks=mark.xfail),
    param(None,None,marks=mark.xfail),
])
def test_any_cmd(git,args,expected):
    assert git.__getattr__(args)(["HEAD"])==expected
    # print(res)

@mark.parametrize("args,expected",[
    param([r"--pretty='format:%ad'","--numstat"],execute_command(cmd_builder("log",main_path.as_posix(),r"--pretty='format:%ad'","--numstat"))),
    param("",execute_command(cmd_builder("log",main_path.as_posix()))),
    param("-asda",None,marks=mark.xfail),
])
def test_any_arg(git,args,expected):
    assert git.log(*args)==expected
    # print(res.split('\n'))
#TODO need to complete test cases as needed
def test_git_grep(git):
    print(git.grep(["-E","-n","-o","-I",f'\"[^a-zA-Z0-9_]+\\s*({"|".join(["TODO","FIXME"])}).+\"']))