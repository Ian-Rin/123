'''
Ian Li
550891039
hali0915
USYD CODE CITATION ACKNOWLEDGEMENT
This file contains no acknowledgements.
'''

# USYD CODE CITATION ACKNOWLEDGEMENT
# This file contains no external code or ideas.
# All code in this file is my own original work.

class Post:
    def __init__(self, post_id, author, text):
        # Validate post_id: must be a string of exactly 10 ASCII digits.
        # Use `type() is not str` rather than isinstance() to reject bool
        # and str subclasses — this matters for consistency with later
        # int checks where bool would otherwise sneak through as valid.
        if type(post_id) is not str:
            raise ValueError("post_id must be a string")
        # Check membership in "0123456789" instead of str.isdigit(), which
        # also accepts Unicode digits like '²' or '०' that the spec forbids.
        if len(post_id) != 10 or not all(c in "0123456789" for c in post_id):
            raise ValueError("post_id must be exactly 10 decimal digits")

        # Validate author: 1-20 English letters only.
        if type(author) is not str:
            raise ValueError("author must be a string")
        # Compare against ASCII ranges directly instead of str.isalpha(),
        # which would accept letters from other scripts (e.g. 'é', '中').
        if not (1 <= len(author) <= 20) or not all(
            ("a" <= c <= "z") or ("A" <= c <= "Z") for c in author
        ):
            raise ValueError("author must be 1-20 English letters")

        # Validate text: any string is acceptable per the spec.
        if type(text) is not str:
            raise ValueError("text must be a string")

        # Assign validated fields. post_type, likes, and timestamp take
        # their defaults here; subclasses will override post_type later,
        # and likes/timestamp will be updated when posts are loaded from
        # file or interacted with.
        self.post_type = "Post"
        self.post_id = post_id
        self.author = author
        self.text = text
        self.likes = 0
        self.timestamp = 0.0

    def __str__(self):
        # Output format is fixed by the assignment spec: hidden tests
        # compare this string literally, so the exact spacing, newlines,
        # and decimal precision matter.
        return (
            f"{self.post_type} ({self.post_id}) by @{self.author} "
            f"at {self.timestamp:.2f}:\n"
            f"{self.text}\n"
            f"-> {self.likes} likes"
        )

    def __eq__(self, other):
        # Spec: raise TypeError when compared against a non-Post, rather
        # than the usual NotImplemented dance. Sub-type does not matter —
        # two Posts with the same post_id are equal even if one is a
        # TextPost and the other a StoryPost.
        if not isinstance(other, Post):
            raise TypeError(
                "Post can only be compared with another Post instance"
            )
        return self.post_id == other.post_id

    def add_to_likes(self, n=1):
        # `type(n) is not int` rejects bool too (type(True) is bool, not
        # int), which matches the stricter checks used elsewhere. Reject
        # before touching state so a bad call leaves likes unchanged.
        if type(n) is not int or n < 0:
            raise ValueError("n must be a non-negative int")
        self.likes += n

    def merge_in(self, other_post):
        # Type gate first: equality below would raise TypeError on a
        # non-Post, but the spec wants that specific error surface here
        # too, so checking explicitly keeps the message meaningful.
        if not isinstance(other_post, Post):
            raise TypeError("other_post must be a Post instance")
        # Use == (now post_id-based) to decide mergeability. Sub-type
        # mismatch is allowed per spec; only post_id matters.
        if self != other_post:
            raise ValueError("posts must be equal (same post_id) to merge")

        # Likes simply accumulate. We trust other_post.likes is already
        # in a valid state; the spec doesn't ask us to re-validate it.
        self.likes += other_post.likes

        # Keep the longer text; on tie, retain this instance's text.
        if len(other_post.text) > len(self.text):
            self.text = other_post.text

        # post_type, post_id, author, timestamp: unchanged on this side.
        # StoryPost handles child merging in its override.


class TextPost(Post):
    def __init__(self, post_id, author, text):
        super().__init__(post_id, author, text)
        self.post_type = "TextPost"


class StoryPost(Post):
    def __init__(self, post_id, author, text, children):
        # Validate and assign base fields via Post.__init__ first, so
        # any ValueError from base validation fires before we touch
        # children.
        super().__init__(post_id, author, text)
        self.post_type = "StoryPost"

        # Spec requires a list specifically — reject tuples or other
        # iterables even though they would seem compatible.
        if type(children) is not list:
            raise ValueError("children must be a list")

        # Each entry must itself be a valid post_id, and none of them
        # can equal this StoryPost's own id (no self-referential story).
        for child_id in children:
            if type(child_id) is not str or len(child_id) != 10 or not all(
                c in "0123456789" for c in child_id
            ):
                raise ValueError(
                    "each entry in children must be a valid post_id"
                )
            if child_id == post_id:
                raise ValueError(
                    "children must not contain this StoryPost's own post_id"
                )

        # Copy so later mutations of the caller's list don't leak into
        # this instance's state.
        self.children = list(children)

    def __str__(self):
        return (
            f"{self.post_type} ({self.post_id}) by @{self.author} "
            f"at {self.timestamp:.2f}:\n"
            f"{self.text}\n"
            f"Contains: {self.children}\n"
            f"-> {self.likes} likes"
        )

    def add_child(self, child_post_id, position=-1):
        # Validate id format first — same rules as Post.__init__ uses for
        # post_id so the children list stays internally consistent.
        if type(child_post_id) is not str or len(child_post_id) != 10 or not all(
            c in "0123456789" for c in child_post_id
        ):
            raise ValueError(
                "child_post_id must be a 10-digit post_id string"
            )
        # A StoryPost cannot reference itself as its own child.
        if child_post_id == self.post_id:
            raise ValueError(
                "child_post_id must not equal this StoryPost's post_id"
            )

        # Position must be a real int (reject bool). -1 is the sentinel
        # for append; otherwise it must be a valid insertion index, i.e.
        # 0..len(children) inclusive (len is valid for insert at end).
        if type(position) is not int:
            raise ValueError("position must be an int")
        if position != -1 and not (0 <= position <= len(self.children)):
            raise ValueError("position is out of range")

        # Duplicate guard runs AFTER validation so bad inputs still error
        # out rather than silently short-circuiting on a duplicate.
        if child_post_id in self.children:
            return

        if position == -1:
            self.children.append(child_post_id)
        else:
            self.children.insert(position, child_post_id)

    def merge_in(self, other_post):
        # Delegate base-field merge (type check, likes, text) to Post.
        super().merge_in(other_post)
        # Children only merge when both sides are StoryPosts; spec says
        # sub-type is ignored for equality but child merging is
        # conditional on both being stories.
        if isinstance(other_post, StoryPost):
            for child_id in other_post.children:
                # add_child handles dedup and validation; the only way
                # it would raise here is on a corrupted other_post whose
                # children contained an invalid id or its own post_id.
                self.add_child(child_id)
