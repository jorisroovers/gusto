var mealplan = new Vue({
    el: '#mealplan',
    created() {
        this.fetchData();
    },
    data: {
        mealplan: []
    },
    methods: {
        regen(meal_index) {
            const self = this
            axios.post('/api/regen', {
                "meal_index": meal_index
            }).then(function () {
                self.fetchData()
            })
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
                    for (meal of response.data.mealplan) {
                        console.log(meal);
                        self.mealplan.push({
                            "weekday": moment(meal.date).format('dddd'),
                            "date": moment(meal.date).format('YYYY-MM-DD'),
                            "recipe": meal.recipe.Name,
                            "tags": meal.recipe['parsed-tags']
                        })

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