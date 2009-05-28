""" Telekommunisten Integration Environment 
    Git Access Objects

    These classes provide an interface to a 
    git repository.

    Dmytri Kleiner <dk@telekommunisten.net>
"""

from shell import ShellAccessObject

class GitAccessObject(ShellAccessObject):
    """ Provides access methods to git subprocesses
        with environment variable injection

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> g = GitAccessObject()
        >>> g.setEnv("GIT_DIR", gitDir)
        >>> command = ["git","config", "core.bare"]
        >>> g.access(command).upper()
        'TRUE'
    """
    def __init__(self, gitDir=None):
        ShellAccessObject.__init__(self) 
        if gitDir:
            self.setEnv("GIT_DIR", gitDir)

    def getCommit(self, hash):
        """ Retrieve a GitCommit object

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> g.getCommit(initHash)
            GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
        """
        return GitCommit(self, hash)
    def getRef(self, hash):
        """ Retrieve a GitRef Object

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initRef = "tags/init"
            >>> g.getRef(initRef)
            GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e tags/init]
        """
        return GitRef(self, hash)

class GitCommit():
    """ Provides information about a git commit
    """

    def __init__(self, accessObject, hash):
        """ Initialize with GitAccessObject and Git commit 
            Object name (sha1 hash)

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> GitCommit(g, initHash)
            GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
        """
        self.git = accessObject
        self.hash = hash
    def committerName(self):
        """ Name of committer

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = g.getCommit(initHash)
            >>> c.committerName()
            'Dmytri Kleiner'
        """
        info = self.git.access(["git","show", "--pretty=format:%cn", self.hash]) 
        return info.split("\n")[0]
    def pathExists(self, path):
        """ Verify path exists in object's tree 

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = g.getCommit(initHash)
            >>> c.pathExists("README")
            True
            >>> c.pathExists("MISSINGFILE")
            False
        """
        pathTest = self.git.access(["git", "ls-tree", "--name-only", self.hash, path]) 
        found = False
        if pathTest == path:
            found = True
        return found
    def tag(self, tagName):
        """ Create a tag 

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = g.getCommit(initHash)
            >>> from datetime import datetime
            >>> tagName = "testTag"
            >>> c.tag(tagName)
            >>> r = g.getRef("tags/%s" % tagName)
            >>> r.hash()
            'd3bb1c687114d0c59e82ce1c9a1b423c1e0f154e'
            >>> g.access(["git", "tag", "-d", tagName])
            "Deleted tag 'testTag'"
        """
        self.git.setEnv("EDITOR", "")
        self.git.access(["git", "tag", tagName, self.hash])
    def __str__(self):
        return "GitCommit [%s]" % self.hash

class GitRef():
    """ Provides information about a specific git
        reference from the ref name
    """
    def __init__(self, accessObject, refName):
        """ Initialize a GitRef with GitAccessObject and ref name

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> refName = "refs/tags/init"
            >>> GitRef(g, refName)
            GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e refs/tags/init]
        """
        self.git = accessObject
        self.refName = refName
    def isBranch(self):
        """ Is this ref a branch?

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> r = g.getRef("refs/tags/init")
            >>> r.isBranch()
            False
            >>> r = g.getRef("refs/heads/master")
            >>> r.isBranch()
            True
        """
        branch = False
        if "refs/heads/" == self.refName[:11]:
            branch = True
        return branch
    def isMaster(self):
        """ Is this ref the master branch?

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> r = g.getRef("refs/tags/init")
            >>> r.isMaster()
            False
            >>> r = g.getRef("refs/heads/master")
            >>> r.isMaster()
            True
        """
        master = False
        if "refs/heads/master" == self.refName:
            master = True
        return master
    def hash(self):
        """ Return the object name (sha1 hash) for the ref
            
            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> refName = "refs/tags/init"
            >>> g = GitAccessObject(gitDir).getRef(refName)
            >>> g.hash()
            'd3bb1c687114d0c59e82ce1c9a1b423c1e0f154e'
        """
        return self.git.access(["git", "show-ref", "-s", self.refName])
    def getCommit(self):
        """ Return a GitCommit object

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> refName = "refs/tags/init"
            >>> g = GitAccessObject(gitDir).getRef(refName)
            >>> g.getCommit()
            GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
        """
        return GitCommit(self.git, self.hash())
    def __repr__(self):
        return "GitRef [%s %s]" % (self.hash(), self.refName)


