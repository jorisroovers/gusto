class Tag {
    // TODO
}

class Recipe {
    constructor(id, name, description, comments, url, tags) {
        this.id = id
        this.name = name
        this.description = description
        this.comments = comments
        this.url = url
        this.tags = tags
    }

    static fromJSON(data) {
        return new Recipe(data.id, data.name, data.description, data.comments, data.url, data.tags)
    }

}

class Meal {
    // TODO

    construct(data) {
        this.data = data
    }

}

