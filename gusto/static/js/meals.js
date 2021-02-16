

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
            const self = this
            axios.delete(`/api/meal/${this.meal.id}`).then(function (response) {
                console.log("deleted meal")
                self.$emit('reloadMeal');
            })
        },
    },
    template: `
    <tr>
        <td class="no-wrap">{{ meal.date.format('dddd') }}</td>
        <td class="no-wrap">{{ meal.date.format('YYYY-MM-DD') }}</td>
        <td>
            <a v-if="meal.recipe && meal.recipe.url" :href="meal.recipe.url" target="_blank">
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
    props: ['recipes', "initialItem"],
    data: function () {
        return { isActive: false, selectedItem: this.initialItem }
    },
    computed: {
        classObject: function () {
            return { 'is-active': this.isActive }
        },
    },
    methods: {
        selectRecipe: function (recipe) {
            this.selectedItem = recipe
            this.isActive = false
            this.$emit('selected', this.selectedItem);
        }
    },
    template: `
    <div class="dropdown" v-bind:class="classObject" >
    <div class="dropdown-trigger" v-on:click="isActive=!isActive">
        <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
        <span v-if="selectedItem==null">Select a recipe</span>
        <span v-else>{{selectedItem.name}}</span>
        <span class="icon is-small">
            <i class="fas fa-angle-down" aria-hidden="true"></i>
        </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
        <input type="input"> 
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
        return { recipes: [], chosenRecipe: this.meal.recipe }
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
            this.chosenRecipe = newRecipe
            // this.$set(this., 'recipe', newRecipe)
        },
        save() {
            const self = this
            console.log(self.meal)
            if (self.meal.recipe == null) {
                console.log("Saving new meal", self.meal, self.chosenRecipe.id)
                axios.post('/api/meals', {
                    "meal": { "date": self.meal.date.format('YYYY-MM-DD'), "recipe_id": self.chosenRecipe.id }
                }).then(function (response) {
                    self.$emit('reloadMeal');
                })
            } else {
                console.log("Updating existing meal", self.meal.id)
                axios.put(`/api/meal/${self.meal.id}`, {
                    "recipe_id": this.chosenRecipe.id
                }).then(function (response) {
                    self.$emit('reloadMeal');
                })
            }


        }
    },
    template: `
    <tr>
        <td class="no-wrap">{{ meal.date.format('dddd') }}</td>
        <td class="no-wrap">{{ meal.date.format('YYYY-MM-DD') }}</td>
        <td><recipe-selector v-bind:recipes="recipes" v-bind:initialItem="chosenRecipe" @selected="recipeChanged" /></td>
        <td></td>
        <td><template v-if="chosenRecipe"><recipe-tag v-bind:tag="tag" v-for="tag in chosenRecipe.tags" /></template></td>
        <td><button class="button" :disabled="chosenRecipe == null" v-on:click="save()">Save</button></td>
    </tr>
    `
})


Vue.component('meal-row', {
    props: ['meal'],
    data: function () {
        return { editing: this.meal.recipe == null, editableMeal: this.meal }
    },
    computed: {
        classObject: function () {
            return { 'is-today': this.editableMeal.date.isSame(new Date(), 'day') }
        },
    },
    methods: {
        editMeal() {
            console.log("Editing meal")
            this.editing = true;
        },
        reloadMeal() {
            const dateStr = this.editableMeal.date.format('YYYY-MM-DD')
            const self = this
            axios.get('/api/meal', { params: { date: dateStr } })
                .then(function (response) {
                    console.log("reload meal", response.data)
                    if (response.data.meal == null) {
                        // this.$set(this., 'recipe', newRecipe)
                        self.editableMeal = new PlaceHolderMeal(dateStr)
                    } else {
                        self.$set(self, 'editableMeal', Meal.fromJSON(response.data.meal))
                        // this.editableMeal = Meal.fromJSON(response.data.meal)
                    }
                    self.editing = false
                })
        }
    },
    template: `
        <meal-row-edit v-bind:class="classObject" v-bind:meal="editableMeal" @reloadMeal="reloadMeal()" v-if="this.editing" />
        <meal-row-placeholder v-bind:class="classObject" v-bind:meal="editableMeal" @reloadMeal="reloadMeal()" v-else-if="this.editableMeal.recipe == null" />
        <meal-row-normal v-bind:class="classObject" v-bind:meal="editableMeal" @reloadMeal="reloadMeal()" @editMeal="editMeal()" v-else />
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
                mealplanMap[dayStr] = new PlaceHolderMeal(day)
                day = moment(day).add(1, 'days')
            }

            // fetch meals, replace placeholders with meals if they exist
            axios.get('/api/meals',
                { params: { after: self.start_date.format('YYYY-MM-DD'), before: self.end_date.format('YYYY-MM-DD') } })
                .then(function (response) {
                    for (meal of response.data.meals) {
                        let mealObj = Meal.fromJSON(meal)
                        mealplanMap[mealObj.date.format('YYYY-MM-DD')] = mealObj
                    }
                    self.mealplan = Object.values(mealplanMap)
                })

        }
    }
})