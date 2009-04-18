""" Telekommunisten Integration Environment Git Access Objects
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
    class Errors:
        class CommandFailed(Exception):
            def __init__(self, command, err, code):
                self.command = command
                self.err = err
                self.code = code
            def __str__(self):
                return "Command %s failed: %s (%s)" % \
                        (self.command, self.err, self.code)
    def __init__(self, gitDir=None):
        self.env = None
        if gitDir:
            self.setEnv('GIT_DIR', gitDir)
    def setEnv(self, key, value):
        if None == self.env:
            import os
            self.env = os.environ.copy()
        self.env[key] = value
    def access(self, command):
        sub = Popen(command, env=self.env, stdout=PIPE)
        if sub.returncode:
            raise self.CommandError(str(command),
                    sub.stderr,
                    sub.returncode)
        response = sub.communicate()[0].strip()
        return response
    def getCommit(self, hash):
        """ Create a GitCommit Object

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> g.getCommit(initHash)
            GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
        """
        return GitCommit(self, hash)
    def getRef(self, hash):
        """ Create a GitRef 

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initRef = "tags/init"
            >>> g.getRef(initRef)
            GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e tags/init]
        """
        return GitRef(self, hash)

class GitCommit():
    """ Provides information about a specific git
        commit object from the Object Name (sha1 hash)

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> g = GitAccessObject(gitDir)
        >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
        >>> GitCommit(g, initHash)
        GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]
    """
    def __init__(self, accessObject, hash):
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
            >>> c.pathExists('README')
            True
            >>> c.pathExists('MISSINGFILE')
            False
        """
        pathTest = self.git.access(["git", "ls-tree", "--name-only", self.hash, path]) 
        found = False
        if pathTest == path:
            found = True
        return found
    def tag(self, tagName):
        """
            Create a Tag from an Object Name (sha1 hash)

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> c = g.getCommit(initHash)
            >>> from datetime import datetime
            >>> tagDate = datetime.now().isoformat()
            >>> c.tag(tagDate)
            >>> r = g.getRef("tags/%s" % tagDate)
            >>> r.hash()
            'd3bb1c687114d0c59e82ce1c9a1b423c1e0f154e'
        """
        tagged = False
        if self.git.access(["git", "tag","-a", self.hash, tagName]) == 0:
            tagged = True
        return tagged
    def __repr__(self):
        return "GitCommit [%s]" % self.hash

class GitRef():
    """ Provides information about a specific git
        reference from the ref name

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> g = GitAccessObject(gitDir)
        >>> refName = "refs/tags/init"
        >>> GitRef(g, refName)
        GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e refs/tags/init]
    """
    def __init__(self, accessObject, refName):
        self.git = accessObject
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
        return self.git.access(["git", "show-ref", "-s", self.refName])
    def getCommitObject(self):
        return gitCommitObject(self.hash())
    def __repr__(self):
        return "GitRef [%s %s]" % (self.hash(), self.refName)

# TEST CODE

import unittest

class TestGitAccessObject(unittest.TestCase):
    def testSetEnv(self):
        g = GitAccessObject('/dev/null')
        self.assert_('GIT_DIR' in g.env)
        self.assert_('PATH' in g.env)
        self.assert_('PWD' in g.env)
        self.assertEqual(g.env['GIT_DIR'], '/dev/null')
        g = GitAccessObject()
        self.assertEqual(g.env, None)
        g.setEnv('TEST', 'TESTING')
        self.assert_('PATH' in g.env)
        self.assert_('PWD' in g.env)
        self.assertEqual(g.env['TEST'], 'TESTING')
    def testAccess(self):
        g = GitAccessObject('/dev/null')
        command = ['echo','TESTING']
        stdout = g.access(command)
        self.assertEqual(stdout, 'TESTING')
       

class FakeGitAccessObject(GitAccessObject):
    def __init__(self, gitDir=None):
        GitAccessObject.__init__(self, gitDir)
        self.response = None
    def setAccessResponse(self, str):
        self.response = str.strip()
    def access(self, command):
        return self.response

class TestGitAccessObjectWithFake(unittest.TestCase):
    def setUp(self):
        self.git = FakeGitAccessObject('/dev/null')
        initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
        self.commit = self.git.getCommit(initHash)
        initRef = "tags/init"
        self.ref = self.git.getRef(initRef)
    def testGetCommit(self):
        assertRepr = "GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]"
        refRepr = str(self.commit)
        self.assertEqual(refRepr, assertRepr)
    def testGetRef(self):
        assertRepr = "GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e tags/init]"
        self.git.setAccessResponse("d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e")
        refRepr = str(self.ref)
        self.assertEqual(refRepr, assertRepr)
    def testCommitterName(self):
        fakeShow = \
"""
Dmytri Kleiner
diff --git a/README b/README
new file mode 100644
index 0000000..4337545
"""
        self.git.setAccessResponse(fakeShow)
        self.assertEqual(self.commit.committerName(), "Dmytri Kleiner")
    def testPathExists(self):
        self.git.setAccessResponse("README")
        self.assert_(self.commit.pathExists("README"))
    def testTag(self):
        self.commit.tag('test')
        r = self.git.getRef('tags/test')
        self.git.setAccessResponse(self.commit.hash)
        self.assertEqual(r.hash(), self.commit.hash)

def _docTest():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
        _docTest()
        
