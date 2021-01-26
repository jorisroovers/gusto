var mealplan = new Vue({
    el: '#mealplan',
    created() {
        this.changeWeek("today")
    },
    data: {
        start_date: null,
        mealplan: []
    },
    methods: {
        regenMealPlan(meal_index) {
            const self = this
            axios.post('/api/regen_mealplan', {
                "start_date": self.start_date
            }).then(function () {
                self.fetchData()
            })
        },
        regenMeal(meal_index) {
            const self = this
            axios.post('/api/regen_meal', {
                "meal_index": meal_index
            }).then(function () {
                self.fetchData()
            })
        },
        changeWeek(weekIncrease) {
            console.debug("changeWeek:", weekIncrease);
            if (weekIncrease === "today") {
                this.start_date = moment().startOf('week').day('Monday')
            } else {
                this.start_date.add(weekIncrease, 'weeks').startOf('week').day('Monday')
            }
            this.end_date = moment(this.start_date).add(1, 'weeks')
            this.fetchData()
        },
        exportMealplan() {
            const self = this

            axios.post('/api/export').then(function () {
                console.log("export: done");
            })
        },
        fetchData() {
            console.debug("fetchData");
            this.mealplan = []
            const self = this
            axios.get('/api/meals',
                { params: { after: self.start_date.format('YYYY-MM-DD'), before: self.end_date.format('YYYY-MM-DD') } })
                .then(function (response) {
                    for (meal of response.data.meals) {
                        meal.date = moment(meal.date)
                        self.mealplan.push(meal);
                    }
                })
        }
    }
})

var recipes = new Vue({
    el: '#recipes',
    created() {
        this.fetchData();
    },
    data: {
        recipes: [],
        recipeNameFilter: "",
        recipeTagFilter: "",
    },
    // Note: `computed` does NOT work in nested rendering loops (so when you use a v:for inside another v:for)
    // in that case you need to call a function
    computed: {
        filteredRecipes: function () {
            const recipeNameFilter = this.recipeNameFilter.toLowerCase()
            const recipeTagFilter = this.recipeTagFilter.toLowerCase()
            return this.recipes.filter(function (recipe) {
                const nameMatch = recipeNameFilter == "" || recipe.name.toLowerCase().indexOf(recipeNameFilter) >= 0
                let allTagMatch = true;
                if (recipeTagFilter != "") {
                    for (tagFilter of recipeTagFilter.split("+")) {
                        tagMatch = false;
                        for (tag of recipe.tags) {
                            tagMatch = tagMatch || tag.display_name.toLowerCase().indexOf(tagFilter) >= 0
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
                    self.recipes = response.data.recipes
                })
        },
        addTagFilter(tag) {
            if (this.recipeTagFilter == "") {
                this.recipeTagFilter += tag.display_name
            } else {
                this.recipeTagFilter += "+" + tag.display_name
            }
        }
    }
});