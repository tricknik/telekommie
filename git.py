""" Telekommunisten Integration Environment 
    Git Access Objects

    These classes provide an interface to a 
    git repository.

    Dmytri Kleiner <dk@telekommunisten.net>
"""

from subprocess import PIPE, Popen, call

class GitAccessObject():
    """ Provides access methods to git subprocesses
        with environment variable injection

        >>> gitDir = "/etc/telekommie/tests/telekommie.git"
        >>> g = GitAccessObject()
        >>> g.setEnv("GIT_DIR", gitDir)
        >>> command = ["git","config", "core.bare"]
        >>> g.access(command).upper()
        'TRUE'
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
            self.setEnv("GIT_DIR", gitDir)
    def setEnv(self, key, value):
        """ Set environment variable

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> g.setEnv("TEST", "TESTING")
            >>> g.env["TEST"]
            'TESTING'
        """
        if None == self.env:
            import os
            self.env = os.environ.copy()
        self.env[key] = value
    def access(self, command):
        """ Execute shell command and return response

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> command = ["echo","TESTING"]
            >>> g.access(command)
            'TESTING'
        """
        sub = Popen(command, env=self.env, stdout=PIPE)
        if sub.returncode:
            raise self.CommandError(str(command),
                    sub.stderr,
                    sub.returncode)
        response = sub.communicate()[0].strip()
        return response
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
        """
            Create a tag 

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
    def __repr__(self):
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

# TEST CODE

import unittest

class FakeGitAccessObject(GitAccessObject):
    """ Testing double for GitAccessObject 
    """
    def __init__(self, gitDir=None):
        GitAccessObject.__init__(self, gitDir)
        self.response = None
    def setAccessResponse(self, str):
        """ What to return when access is called

            >>> g = FakeGitAccessObject()
            >>> g.setAccessResponse("IT'S ALWAYS SIX O'CLOCK?!")
            >>> g.access(["What is the time in Akademgorod?"])
            "IT'S ALWAYS SIX O'CLOCK?!"
        """
        self.response = str.strip()
    def access(self, command):
        """ Always return what is set by setAccessResponse
        """
        return self.response

class TestFakeGitAccessObject(unittest.TestCase):
    def setUp(self):
        """ Instantiate a FakeGitAccessObject double for testing
        """
        self.git = FakeGitAccessObject()
        initHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
        self.commit = self.git.getCommit(initHash)
        initRef = "tags/init"
        self.ref = self.git.getRef(initRef)

    # GitAccessObject Tests

    def testSetEnv(self):
        """ Test Set Environment Variable
        """
        self.git.setEnv("TEST", "TESTING")
        self.assertEqual(self.git.env["TEST"],"TESTING")
    def testGetCommit(self):
        """ Verify getCommit returned a GitCommit object
        """
        assertRepr = "GitCommit [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e]"
        refRepr = str(self.commit)
        self.assertEqual(refRepr, assertRepr)
    def testGetRef(self):
        """ Verify getRef returned a GitRef object
        """
        assertRepr = "GitRef [d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e tags/init]"
        self.git.setAccessResponse("d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e")
        refRepr = str(self.ref)
        self.assertEqual(refRepr, assertRepr)

    # GitCommit Tests

    def testCommitterName(self):
        """ Parse Committer Name from git info response
        """
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
        """ Verify GitCommit.pathExists works with double
        """
        self.git.setAccessResponse("README")
        self.assert_(self.commit.pathExists("README"))
    def testTag(self):
        """ Verify GitRef.hash method works with double
        """
        self.commit.tag("test")
        r = self.git.getRef("tags/test")
        self.git.setAccessResponse(self.commit.hash)
        self.assertEqual(r.hash(), self.commit.hash)

    # GitRef Tests

    def testGetCommit(self):
        """ Test GitRef.getCommit returns a GitCommit Objet
        """
        self.git.setAccessResponse("d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e")
        c = self.ref.getCommit()
        self.assertEqual(c.hash, self.commit.hash)
    def testHash(self):
        """ Test GitRef.hash returns the object name (sha1 hash)
        """
        self.git.setAccessResponse("d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e")
        self.assertEqual(self.ref.hash(), self.commit.hash)
    def testIsBranch(self):
        """ Test GitRef.isBranch returns False for ref "tags/init"
        """
        self.assertEqual(self.ref.isBranch(), False)
    def testIsMaster(self):
        """ Test GitRef.isMaster returns False for ref "tags/init"
        """
        self.assertEqual(self.ref.isMaster(), False)


def _docTest():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
        _docTest()
        
