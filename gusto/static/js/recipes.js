var recipes = new Vue({
    el: '#recipes',
    created() {
        this.fetchData();
    },
    data: {
        recipes: [],
        recipeNameFilter: "",
        recipeTagFilter: [],
        newRecipeName: "",
        newRecipeTags: [],
    },
    // Note: `computed` does NOT work in nested rendering loops (so when you use a v:for inside another v:for)
    // in that case you need to call a function
    computed: {
        filteredRecipes: function () {
            const recipeNameFilter = this.recipeNameFilter.toLowerCase()
            const self = this
            return this.recipes.filter(function (recipe) {
                const nameMatch = recipeNameFilter == "" || recipe.name.toLowerCase().indexOf(recipeNameFilter) >= 0
                let allTagMatch = true;
                if (self.recipeTagFilter.Length != 0) {
                    for (tagFilter of self.recipeTagFilter) {
                        tagMatch = false;
                        for (tag of recipe.tags) {
                            tagMatch = tagMatch || tag.display_name.toLowerCase().indexOf(tagFilter.display_name.toLowerCase()) >= 0
                        }
                        allTagMatch = allTagMatch && tagMatch;
                    }
                }
                return nameMatch && allTagMatch;
            })
        }
    },
    methods: {
        fetchData() {
            console.log("fetchData -- recipes")
            this.recipes = []
            const self = this
            axios.get('/api/recipes')
                .then(function (response) {
                    for (recipeData of response.data.recipes) {
                        self.recipes.push(Recipe.fromJSON(recipeData))
                    }
                })
        },
        addTagFilter(tag) {
            this.recipeTagFilter.push(tag);
        },
        removeTagFilter(tag) {
            this.recipeTagFilter = this.recipeTagFilter.filter(item => item !== tag)
        },
        addRecipe() {
            const self = this;
            console.log("adding recipe", this.newRecipeName, this.newRecipeTags)
            axios.post('/api/recipes', {
                "name": this.newRecipeName
            }).then(function (response) {
                console.log(response)
                self.fetchData()
            })

        },
        deleteRecipe(recipe) {
            console.log("deleting", recipe.name);
            const self = this
            if (confirm("Are you sure you want to delete this recipe?")) {
                console.log("Actually deleting:", recipe.id);
                axios.delete('/api/recipes/' + recipe.id)
                    .then(function (response) {
                        self.fetchData()
                    })
            }

        }
    }
});