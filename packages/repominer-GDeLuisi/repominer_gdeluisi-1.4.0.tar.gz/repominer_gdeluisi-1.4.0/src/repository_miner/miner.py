from .git import Git
from .utility import Call
from .helper import cmd_builder,log_builder,rev_list_builder,get_head_commit,is_dir_a_repo,is_git_available
from .exceptions import *
from .data_typing import *
from functools import partial
from typing import Iterable,Optional,Generator
from datetime import datetime
import re
class RepoMiner():
    def __init__(self,path:str):
        self.git=Git(path)
        self.path=path
    #pickle interface methods for multiprocessing compatibility
    def __getstate__(self):
        state=self.__dict__.copy()
        return state
    
    def __setstate__(self,state):
        self.__dict__.update(state)
        
    def retrieve_commits(self,from_commit:Optional[str]=None,to_commit:Optional[str]=None,merges:bool=False,max_count:Optional[int]=None,skip:Optional[int]=None,author:Optional[str]=None,follow:Optional[str]=None,since:Optional[datetime]=None,to:Optional[datetime]=None,extra_args:Optional[Iterable[str]]=[])->Generator[CommitInfo,None,None]:
        if not from_commit:
            from_commit=get_head_commit(self.path)
        pretty=r"%H:-#_%T:-#_%s:-#_%an:-#_%ae:-#_%as:-#_%D"
        logs=self.git.log(log_builder(from_commit,to_commit,pretty,merges,max_count,skip,author,follow,since,to,extra_args))
        for log in logs.splitlines(False):
            try:
                c_hash,tree,sub,a_name,a_email,c_date,ref=log.split(r":-#_")
                yield CommitInfoImpl(c_hash,c_hash[:7],tree,ref,sub,a_name,a_email,datetime.strptime(c_date,r"%Y-%m-%d"),Call(self.tree,tree))
            except ValueError as e:
                raise ParsingException(f"Log {log} was not parsed")
    
    def retrieve_commit_list(self,from_commit:Optional[str]=None,to_commit:Optional[str]=None,merges:bool=False,max_count:Optional[int]=None,skip:Optional[int]=None,author:Optional[str]=None,follow:Optional[str]=None,since:Optional[datetime]=None,to:Optional[datetime]=None,extra_args:Optional[Iterable[str]]=[])->list[CommitInfo]:
        return list(self.retrieve_commits(from_commit,to_commit,merges,max_count,skip,author,follow,since,to,extra_args))
    
    def n_commits(self,from_commit:Optional[str]=None,to_commit:Optional[str]=None,merges:bool=True,skip:Optional[int]=None,author:Optional[str]=None,since:Optional[datetime]=None,to:Optional[datetime]=None)->int:
        if not from_commit:
            from_commit=get_head_commit(self.path)
        return int(self.git.rev_list(rev_list_builder(from_commit=from_commit,to_commit=to_commit,merges=merges,max_count=None,skip=skip,author=author,since=since,to=to,args=["--count"])))
                
    def tree(self,treeish:str)->Tree:
        try:
            t=self.git.cat_file(["-t",treeish])
            if t == "blob" and t == "tag":
                raise GitCmdError()
            return TreeImpl(treeish,"",Call(self.iterate_tree,treeish,True))
        except GitCmdError as e:
            raise ValueError(f"Cannot retrieve a tree from {treeish}")
    
    def iterate_tree(self,treeish:str,recursive:bool=False)->Generator[Union[Tree,Blob],None,None]:
        p_format="--format=\"%(objectname)///%(objecttype)///%(objectsize)///%(path)\""
        args=[p_format]
        if recursive:
            args.append("-r")
            args.append("-t")
        args.append(treeish)
        try:
            res=self.git.ls_tree(args)
            for line in res.splitlines(False):
                h,t,size,path=line.split('///')
                if t == "tree":
                    yield TreeImpl(h,path,Call(self.iterate_tree,treeish=treeish,recursive=True))
                elif t == "blob":
                    size=int(size)
                    yield BlobImpl(h,path.rsplit("/",1)[-1],path,size,Call(self.get_source,h))
        except GitCmdError as e:
            raise ValueError(f"Cannot retrieve a tree from {treeish}")
        except ValueError as e:
            raise ParsingException(f"Unable to parse tree line {line}")
        
    def resolve_tree(self,treeish:str,recursive:bool=False)->list[Union[Tree,Blob]]:
        return list(self.iterate_tree(treeish,recursive))
    
    def get_commit(self,commit_sha:str)->CommitInfo:
        pretty=r"%H:-#_%T:-#_%s:-#_%an:-#_%ae:-#_%as:-#_%D"
        log=self.git.log(log_builder(commit_sha,None,pretty,max_count=1))
        c_hash,tree,sub,a_name,a_email,c_date,ref=log.split(r":-#_")
        return CommitInfoImpl(c_hash,c_hash[:7],tree,ref,sub,a_name,a_email,datetime.strptime(c_date,r"%Y-%m-%d"),Call(self.tree,tree))
    
    def local_branches(self)->Generator[Head,None,None]:
        lines=self.git.show_ref(["--branches"]).split("\n")
        for line in lines:
            hash,ref = line.split(" ",1)
            tag=ref.removeprefix("refs/heads/")
            yield HeadImpl(hash=hash,name=tag,retrieve_func=Call(self.retrieve_commits,from_commit=hash,merges=True))

    def get_branch(self,name:str)->Head:
        line=self.git.show_ref(["--branches",name])
        hash,ref = line.split(" ",1)
        tag=ref.removeprefix("refs/heads/")
        return HeadImpl(hash=hash,name=tag,retrieve_func=Call(self.retrieve_commits,from_commit=hash,merges=True))

    def local_branches_list(self)->list[Head]:
        return list(self.local_branches())
    
    def authors(self)->set[Author]:
        pattern=re.compile(r'([A-Za-zÀ-ÖØ-öø-ÿé\s]+) <([a-z0-9A-ZÀ-ÖØ-öø-ÿé!#$%@.&*+\/=?^_{|}~-]+)> \(\d+\)')
        authors=set()
        res=self.git.shortlog(["-e","--all","--pretty=\"format:%H\""])
        res=res.split("\n\n")
        for a_block in res:
            tmp=a_block.split("\n")
            author=tmp.pop(0).strip()
            match=re.match(pattern=pattern,string=author)
            if not match:
                continue
            name,email=match.groups()
            author = Author(email,name,[])
            for line in tmp:
                author.commits_authored.append(line.strip())
            authors.add(author)
        return authors
    
    def get_source(self, id:str)->list[str]:
        try:
            if self.git.cat_file("-t",id) != "blob":
                raise TypeError(f"Hexsha {id} in not a blob")
        except GitCmdError:
            raise FileNotFoundError("Couldn't retrieve the object")
        return re.split(string=self.git.cat_file("-p",id),pattern=r"\r\n|\r|\n")

    def get_tags(self)->Generator[Head,None,None]:
        lines=self.git.show_ref(["--tags"]).split("\n")
        for line in lines:
            hash,ref = line.split(" ",1)
            tag=ref.removeprefix("refs/tags/")
            yield HeadImpl(hash=hash,name=tag,retrieve_func=Call(self.retrieve_commits,from_commit=hash,merges=True))

    def get_tag(self,tag:str)->Head:
        line=self.git.show_ref(["--tags",tag])
        hash,ref = line.split(" ",1)
        tag=ref.removeprefix("refs/tags/")
        return HeadImpl(hash=hash,name=tag,retrieve_func=Call(self.retrieve_commits,from_commit=hash,merges=True))
            