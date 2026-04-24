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

        # Store a copy, not the original reference. Otherwise mutations to the caller's list after construction would leak into this StoryPost's internal state.
        # leak into this instance's state.
        self.children = list(children)

    def __str__(self):
        return (
            f"{self.post_type} ({self.post_id}) by @{self.author} "
            f"at {self.timestamp:.2f}:\n"
            f"{self.text}\n"
            f"Contains: {self.children}\n"
            f"-> {self.likes} likes"
        )
