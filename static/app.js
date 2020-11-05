var app = new Vue({
    el: '#mealplan',
    created() {
        console.log("created")
        this.fetchData();
    },
    data: {
        mealplan: []
    },
    methods: {
        regen() {
            const self = this
            axios.get('/regen').
                then(function () {
                    self.fetchData()
                })
        },
        fetchData() {
            console.log("fetchData")
            this.mealplan = []
            let table_mealplan = this.mealplan
            axios.get('/mealplan')
                .then(function (response) {
                    for (meal of response.data.mealplan) {
                        console.log(meal);
                        table_mealplan.push({
                            "date": meal.date, "recipe": meal.recipe.Name,
                            "labels": meal.recipe.Labels
                        })

                    }
                })
        }
    }
})