class Constraint:
    def __init__(self, name, title: str, match_func = None) -> None:
        self.name = name
        self.title = title
        self.match_func = match_func

    def match(self, recipe: dict) -> bool:
        if self.match_func:
            return self.match_func(recipe)
        return False

    def for_json(self) -> dict:
        return {"id": self.id, "title": self.title}


class TagConstraint(Constraint):

    def __init__(self, name, title , included_tags, excluded_tags) -> None:
        super().__init__(name, title)
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags

    def match(self, recipe: dict) -> bool:
        return all(tag in recipe['parsed-tags'] for tag in self.included_tags) and \
               all(tag not in recipe['parsed-tags'] for tag in self.excluded_tags )

# Hardcoded database of constraints
CONSTRAINTS = dict({
    (tag.name, tag) for tag in [ 
        TagConstraint("veggie-day", "Veggie Dag", ["Vegetarisch"], ["Zondigen", "Overschot", "Exclude"]), 
        TagConstraint("fish-day", "Vis Dag", ["Vis"], ["Zondigen", "Overschot", "Exclude"]), 
        TagConstraint("asian-day", "Asian Dag", ["Asian"], ["Zondigen", "Overschot", "Exclude"]),
        TagConstraint("steak-day", "Steak Dag", ["Steak"], ["Zondigen", "Overschot", "Exclude"]),
        TagConstraint("pasta-day", "Pasta Dag", ["Pasta"], ["Zondigen", "Overschot", "Exclude"]),
        TagConstraint("free-day", "Vrije Dag", [], ["Zondigen", "Overschot", "Exclude"])
    ]
})
