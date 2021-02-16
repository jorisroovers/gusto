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

    constructor(id, date, recipe, constraint) {
        this.id = id
        this.date = moment(date)
        this.recipe = recipe
        this.constraint = constraint
    }

    static fromJSON(data) {
        return new Meal(data.id, data.date, Recipe.fromJSON(data.recipe), data.constraint)
    }

}

class PlaceHolderMeal extends Meal {
    constructor(date) {
        super(null, date, null, null)
    }

}

