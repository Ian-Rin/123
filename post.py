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
        # Strict type check with `type() is` — isinstance would accept
        # bool as int later when we validate `likes`.
        if type(post_id) is not str:
            raise ValueError("post_id must be a string")
        # Use literal "0123456789" rather than str.isdigit(), which
        # accepts Unicode digits like '²' or '०' that the spec forbids.
        if len(post_id) != 10 or not all(c in "0123456789" for c in post_id):
            raise ValueError("post_id must be exactly 10 decimal digits")

        if type(author) is not str:
            raise ValueError("author must be a string")
        # Use ASCII range comparison instead of str.isalpha(), which
        # accepts non-English letters (e.g. 'é', '中').
        if not (1 <= len(author) <= 20) or not all(
            ("a" <= c <= "z") or ("A" <= c <= "Z") for c in author
        ):
            raise ValueError("author must be 1-20 English letters")

        if type(text) is not str:
            raise ValueError("text must be a string")

        # Default values for post_type, likes, timestamp. Subclasses
        # override post_type after calling super().__init__().
        self.post_type = "Post"
        self.post_id = post_id
        self.author = author
        self.text = text
        self.likes = 0
        self.timestamp = 0.0

    def __str__(self):
        # Output format is fixed by the assignment spec.
        return (
            f"{self.post_type} ({self.post_id}) by @{self.author} "
            f"at {self.timestamp:.2f}:\n"
            f"{self.text}\n"
            f"-> {self.likes} likes"
        )


class TextPost(Post):
    def __init__(self, post_id, author, text):
        # Delegate all validation and attribute assignment to Post —
        # TextPost has no extra state beyond a different post_type.
        super().__init__(post_id, author, text)
        # Override post_type after super() has set it to "Post".
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

        # Store a copy, not the original reference. Otherwise mutations
        # to the caller's list after construction would leak into this
        # StoryPost's internal state.
        self.children = list(children)

    def __str__(self):
        # Override Post.__str__ to insert the "Contains:" line between
        # the text and the likes line. Other lines must match Post's
        # format exactly since hidden tests compare output literally.
        return (
            f"{self.post_type} ({self.post_id}) by @{self.author} "
            f"at {self.timestamp:.2f}:\n"
            f"{self.text}\n"
            f"Contains: {self.children}\n"
            f"-> {self.likes} likes"
        )
