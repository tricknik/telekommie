""" Telekommunisten Integration Environment Hooks Model
    Dmytri Kleiner <dk@telekommunisten.net>
"""

from telekommie.scm import gitCommitObject, gitRef

class hooks:

    class Errors:
        class RefDisallowed(Exception):
            def __init__(self, refName):
                self.refName = refName:
            def __str__(self):
                return "Push to %s disallowed" % self.refName;
        class AuthorMismatch(Exception):
            def __init__(self, authorName):
                self.authorName = authorName:
            def __str__(self):
                return "Get your own branch, %s" % self.authorName;
        class TaggingFailed(Exception):
            def __init__(self, refName, tagName):
                self.refName = refName:
                self.tagName = tagName:
            def __str__(self):
                return "Unable to create tag %s from %s" % \
                    (self.refName, self.tagName);

    def update(refName, oldHash, newHash):
        branch = GitRef(refName)
        if  branch.isMaster() or not branch.isBranch():
            raise hooks.Errors.RefDisallowed(refName)
        head = branch.getCommitObject()
        if oldHash != "0" * 40:
            update = GitCommitObject(newHash)
            updateAuthor = update.authorName()
            if head.authorName() != updateAuthor:
                raise hooks.Errors.AuthorMismatch(updateAuthor)
            
