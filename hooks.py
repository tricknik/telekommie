""" Telekommunisten Integration Environment Hooks Model
    Dmytri Kleiner <dk@telekommunisten.net>
"""

from git import GitAccessObject
class Hooks:
    
    class Errors:
        class RefDisallowed(Exception):
            def __init__(self, refName):
                self.refName = refName
            def __str__(self):
                return "Push to %s disallowed" % self.refName
        class CommitterMismatch(Exception):
            def __init__(self, committerName):
                self.committerName = committerName
            def __str__(self):
                return "Get your own branch, %s" % self.committerName
        class TaggingFailed(Exception):
            def __init__(self, refName, tagName):
                self.refName = refName
                self.tagName = tagName
            def __str__(self):
                return "Unable to create tag %s from %s" % \
                    (self.refName, self.tagName)
    @staticmethod
    def checkUpdate(head, update):
            updateCommitter = update.committerName()
            if head.committerName() != updateCommitter:
                raise Hooks.Errors.CommitterMismatch(updateCommitter)

    @staticmethod
    def update(refName, oldHash, newHash, accessObject=None):
        """ Git Update Hook
            
            Verify that update follows telekommie rules:

                * Can not be master
                * Must be branch, not tag
                * If not new branch, committer name must not change

            >>> gitDir = "/etc/telekommie/tests/telekommie.git"
            >>> g = GitAccessObject(gitDir)
            >>> newHash = "d3bb1c687114d0c59e82ce1c9a1b423c1e0f154e"
            >>> Hooks.update("refs/heads/test", "0" * 40, newHash) 
        """

        if None == accessObject:
            accessObject = GitAccessObject();
        branch = accessObject.getRef(refName)
        if  branch.isMaster() or not branch.isBranch():
            raise Hooks.Errors.RefDisallowed(refName)
        head = branch.getCommitObject()
        if oldHash != "0" * 40:
            update = accessObject.getCommitObject(newHash)
            self.checkUpdate(head, update)


# TEST CODE

import unittest

class TestHooks(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(TestHooks, self).__init__(methodName)
        from git import FakeGitAccessObject
        self.git = FakeGitAccessObject()
    def testUpdateMaster(self):
        def tryToUpdateMaster():
            Hooks.update("master","0" * 40, "0" * 40, self.git)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateMaster)
    def testUpdateTag(self):
        def tryToUpdateTag():
            Hooks.update("tags/init","0" * 40, "0" * 40, self.git)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateTag)
    def testChangeCommitter(self):
       def tryToChangeCommitter(self=self):
           from git import FakeGitAccessObject
           fakeShow = \
"""
Monty Cantsin
diff --git a/NEOISM b/NEOISM
new file mode 100644
index 0000000..6666666
"""
           self.git.setAccessResponse(fakeShow)
           head = self.git.getCommit("0"*40)
           other = FakeGitAccessObject()
           fakeShow = \
"""
Dmytri Kleiner
diff --git a/README b/README
new file mode 100644
index 0000000..4337545
"""
           other.setAccessResponse(fakeShow)
           update = other.getCommit("0"*40)
           Hooks.checkUpdate(head, update)
       self.assertRaises(Hooks.Errors.CommitterMismatch, tryToChangeCommitter)

