""" Telekommunisten Integration Environment 
    Hooks Model

    This class implements domain logic methods
    for telekommie git hooks

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
        head = branch.getCommit()
        if oldHash != "0" * 40:
            update = accessObject.getCommit(newHash)
            Hooks.haveMatchingCommitterNames(head, update)

    @staticmethod
    def haveMatchingCommitterNames(head, update):
        """ Given two GitCommit objects, verify that the
            committer name has not changed
        """
        updateCommitter = update.committerName()
        if head.committerName() != updateCommitter:
            raise Hooks.Errors.CommitterMismatch(updateCommitter)


