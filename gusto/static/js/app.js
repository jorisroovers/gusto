
const toggleEditButton = document.querySelector("#toggle-edit-button");
toggleEditButton.addEventListener('click', function (event) {
    for (el of document.querySelectorAll(".edit-control")) {
        el.classList.toggle("hidden");
    }
})


var mealplan = new Vue({
    el: '#websocket',
    data: {
        ws: null,
        status: "NA"
    },
    created() {
        this.ws = new ReconnectingWebSocket("ws://" + window.location.host + "/ws/navigation");
        const self = this
        this.ws.addEventListener('open', function (event) {
            console.log('Websocket Open');
            self.status = "open"
        });

        this.ws.addEventListener('close', function (event) {
            console.log('Websocket Close');
            self.status = "closed"
        });

        this.ws.addEventListener('message', function (event) {
            const data = JSON.parse(event.data);
            console.log('Navigating away', data);
            window.location.href = data.url;
        });
    }
})


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
            day = self.start_date
            let mealplanMap = {}
            while (!day.isSame(self.end_date)) {
                const dayStr = day.format('YYYY-MM-DD')
                mealplanMap[dayStr] = { placeholder: true, date: day }
                day = moment(day).add(1, 'days')
            }

            axios.get('/api/meals',
                { params: { after: self.start_date.format('YYYY-MM-DD'), before: self.end_date.format('YYYY-MM-DD') } })
                .then(function (response) {
                    for (meal of response.data.meals) {
                        meal.date = moment(meal.date)
                        meal.placeholder = false
                        mealplanMap[meal.date.format('YYYY-MM-DD')] = meal
                    }
                    console.log(Object.values(mealplanMap))

                    self.mealplan = Object.values(mealplanMap)
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
                    self.recipes = response.data.recipes
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