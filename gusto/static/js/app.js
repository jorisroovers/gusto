
Vue.component('websocket-status', {
    props: [],
    data: function () {
        return {
            ws: null,
            status: "NA"
        }
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
    },
    template: `
    <div class="navbar-item" id="websocket" v-bind:class="{'open': status == 'open'}">
        <i class="fas fa-circle"></i>
    </div>
    `
})

const navbar = new Vue({
    el: '#navbar',
    methods: {
        reloadPage() {
            location.reload(true)
        },
        toggleEdit() {
            for (el of document.querySelectorAll(".edit-control")) {
                el.classList.toggle("show");
            }
        }
    }
})

Vue.component('recipe-tag', {
    props: ['tag'],
    template: `
    <span class="tag" :data-value="tag.name">
        {{tag.display_name}}
    </span>
    `
})

Vue.component('meal-row-placeholder', {
    props: ['meal'],
    data: function () {
        return {
            count: 0
        }
    },
    template: `
    <tr class="placeholder">
        <td class="no-wrap">{{ meal.date.format('dddd') }}</td>
        <td class="no-wrap">{{ meal.date.format('YYYY-MM-DD') }}</td>
        <td>No meal planned</td>
        <td></td>
        <td></td>
    </tr>
    `
})
Vue.component('meal-row-normal', {
    props: ['meal'],
    data: function () {
        return {
            count: 0
        }
    },
    methods: {
        deleteMeal() {
            console.log("deleting")
            axios.delete(`/api/meal/${this.meal.id}`).then(function (response) {
                console.log(response)
            })
        },
    },
    template: `
    <tr>
        <td class="no-wrap">{{ meal.date.format('dddd') }}</td>
        <td class="no-wrap">{{ meal.date.format('YYYY-MM-DD') }}</td>
        <td>
            <a v-if="meal.recipe.url" :href="meal.recipe.url" target="_blank">
                {{ meal.recipe.name }}
            </a>
            <template v-else>{{ meal.recipe.name }}</template>
            <button class="button" v-on:click="$emit('editMeal')">edit</button>
        </td>
        <td class="no-wrap">{{ meal.constraint == null ? "NA" : meal.constraint.title }}</td>
        <td class="no-wrap">
            <span class="tag" :data-value="tag.name" v-for="tag in meal.recipe.tags">
                {{tag.display_name}}
            </span>
        </td>
        <td><button class="button is-danger" v-on:click="deleteMeal()">Delete</button></td>
    </tr>
    `
})

Vue.component('recipe-selector', {
    props: ['recipes'],
    data: function () {
        return { isActive: false, selectedRecipe: null }
    },
    computed: {
        classObject: function () {
            return { 'is-active': this.isActive }
        }
    },
    methods: {
        selectRecipe: function (recipe) {
            this.selectedRecipe = recipe
            this.isActive = false
            this.$emit('selected', this.selectedRecipe);
        }
    },
    template: `
    <div class="dropdown" v-bind:class="classObject" >
    <div class="dropdown-trigger" v-on:click="isActive=!isActive">
        <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
        <span v-if="selectedRecipe==null">Select a recipe</span>
        <span v-else>{{selectedRecipe.name}}</span>
        <span class="icon is-small">
            <i class="fas fa-angle-down" aria-hidden="true"></i>
        </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
        <a href="#" class="dropdown-item" v-for="recipe in recipes" v-on:click="selectRecipe(recipe)">
            <span>{{ recipe.name }}</span>
            <recipe-tag v-bind:tag="tag" v-for="tag in recipe.tags" />
        </a>
        </div>
    </div>
</div>
    `
})

Vue.component('meal-row-edit', {
    props: ['meal'],
    data: function () {
        return { recipes: [], newMeal: this.meal }
    },
    created() {
        const self = this
        axios.get('/api/recipes')
            .then(function (response) {
                self.recipes = response.data.recipes
            })
    },
    methods: {
        recipeChanged(newRecipe) {
            this.$set(this.newMeal, 'recipe', newRecipe)
        },
        save() {
            axios.post('/api/meals', {
                "meal": { "date": this.newMeal.date.format('YYYY-MM-DD'), "recipe_id": this.newMeal.recipe.id }
            }).then(function (response) {
                console.log(response)
                // self.fetchData()
            })
        }
    },
    template: `
    <tr>
        <td class="no-wrap">{{ meal.date.format('dddd') }}</td>
        <td class="no-wrap">{{ meal.date.format('YYYY-MM-DD') }}</td>
        <td><recipe-selector v-bind:recipes="recipes" @selected="recipeChanged" /></td>
        <td></td>
        <td><template v-if="newMeal.recipe"><recipe-tag v-bind:tag="tag" v-for="tag in newMeal.recipe.tags" /></template></td>
        <td><button class="button" v-on:click="save()">Save</button></td>
    </tr>
    `
})


Vue.component('meal-row', {
    props: ['meal'],
    computed: {
        classObject: function () {
            return { 'is-today': this.meal.date.isSame(new Date(), 'day') }
        },
    },
    methods: {
        editMeal() {
            console.log("Editing meal")
        }
    },
    template: `
        <meal-row-edit v-bind:class="classObject" v-bind:meal="meal" v-if="meal.placeholder" />
        <meal-row-normal v-bind:class="classObject" v-bind:meal="meal" @editMeal="editMeal()" v-else />
    `
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

            // populate every day of the week with placeholders
            day = self.start_date
            let mealplanMap = {}
            while (!day.isSame(self.end_date)) {
                const dayStr = day.format('YYYY-MM-DD')
                mealplanMap[dayStr] = { placeholder: true, date: day }
                day = moment(day).add(1, 'days')
            }

            // fetch meals, replace placeholders with meals if they exist
            axios.get('/api/meals',
                { params: { after: self.start_date.format('YYYY-MM-DD'), before: self.end_date.format('YYYY-MM-DD') } })
                .then(function (response) {
                    for (meal of response.data.meals) {
                        meal.date = moment(meal.date)
                        meal.placeholder = false
                        mealplanMap[meal.date.format('YYYY-MM-DD')] = meal
                    }
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