from git import GitAccessObject, GitCommit, GitRef
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

class Tests(unittest.TestCase):
    """ Unit Tests for Git Access Objects
    """
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
       
