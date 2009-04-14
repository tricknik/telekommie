""" Telekommunisten Integration Environment SCM Access Objects
    Dmytri Kleiner <dk@telekommunisten.net>
"""

from subprocess import PIPE, Popen, call

class GitAccessObject():
    """ Base Class for Git Access Objects
        Provides access methods to git subprocesses
        with environment variable injection

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> g = GitAccessObject()
        >>> g.setEnv('GIT_DIR', gitDir)
        >>> command = ['git','config', 'core.bare']
        >>> print g.access(command).upper()
        TRUE
    """
    env = None

    def setEnv(self, key, value):
        if None == self.env:
            import os
            self.env = os.environ.copy()
        self.env[key] = value
    def access(self, command):
        stdout = Popen(command, 
                    env=self.env,
                    stdout=PIPE).communicate()[0]
        return stdout.strip()

class GitCommitObject(GitAccessObject):
    """ Provides information about a specific git
        commit object from the Object Name (sha1 hash)

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> initRef = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
        >>> c = GitCommitObject(initRef)
        >>> c.setEnv('GIT_DIR', gitDir)
        >>> c
        GitCommitObject [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
    """
    def __init__(self, hash):
        self.hash = hash
    def committerName(self):
        """ Name of committer

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> initRef = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = GitCommitObject(initRef)
            >>> c.setEnv('GIT_DIR', gitDir)
            >>> c.committerName()
            'Dmytri Kleiner'
        """
        info = self.access(["git","show", "--pretty=format:%cn", self.hash]) 
        return info.split("\n")[0]
    def pathExists(self, path):
        """ Verify path exists in object's tree 

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> initRef = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = GitCommitObject(initRef)
            >>> c.setEnv('GIT_DIR', gitDir)
            >>> c.pathExists('README')
            True
            >>> c.pathExists('MISSINGFILE')
            False
        """
        pathTest = self.access(["git", "ls-tree", "--name-only", self.hash, path]) 
        found = False
        if pathTest == path:
            found = True
        return found
    def tag(self, hash, tagName):
        tagged = False
        if call(["git", "tag", hash, tagName]) == 0:
            tagged = True
        return tagged
    def __repr__(self):
        return "GitCommitObject [%s]" % self.hash

class GitRef(GitAccessObject):
    """ Provides information about a specific git
        reference from the ref name

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> refName = "refs/tags/init"
        >>> c = GitRef(refName)
        >>> c.setEnv('GIT_DIR', gitDir)
        >>> c
        GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e refs/tags/init]
    """
    def __init__(self, refName):
        self.refName = refName
    def isBranch(self):
        branch = False
        if 'refs/heads/' == self.refName[:11]:
            branch = True
        return branch
    def isMaster(self):
        master = False
        if 'refs/heads/master' == self.refName:
            master = True
        return master
    def hash(self):
        return self.access(["git", "show-ref", "-s", self.refName])
    def getCommitObject(self):
        return gitCommitObject(self.hash())
    def __repr__(self):
        return "GitRef [%s %s]" % (self.hash(), self.refName)

#def _Test():
#    import doctest
#    doctest.testmod()
#
#if __name__ == "__main__":
#        _Test()

