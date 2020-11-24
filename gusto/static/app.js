var mealplan = new Vue({
    el: '#mealplan',
    created() {
        this.changeWeek("today")
        // this.fetchData();
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
            if (weekIncrease === "today") {
                this.start_date = moment().startOf('week').day('Monday')
            } else {
                this.start_date = this.start_date.add(weekIncrease, 'weeks').startOf('week').day('Monday')
            }
            // TODO: remove the regenMealplan() call here, we should just fetch here, not regen
            this.regenMealPlan();
        },
        exportMealplan() {
            const self = this

            axios.post('/api/export').then(function () {
                console.log("export: done");
            })
        },
        fetchData() {
            this.mealplan = []
            const self = this
            axios.get('/api/mealplan')
                .then(function (response) {
                    for (meal of response.data.mealplan.meals) {
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
        recipes: []
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
        }
    }
});