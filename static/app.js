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
        regen(meal_index) {
            const self = this
            axios.post('/api/regen', {
                "meal_index": meal_index
            }).then(function () {
                self.fetchData()
            })
        },
        fetchData() {
            console.log("fetchData")
            this.mealplan = []
            let table_mealplan = this.mealplan
            axios.get('/api/mealplan')
                .then(function (response) {
                    for (meal of response.data.mealplan) {
                        console.log(meal);
                        table_mealplan.push({
                            "weekday": moment(meal.date).format('dddd'),
                            "date": moment(meal.date).format('YYYY-MM-DD'),
                            "recipe": meal.recipe.Name,
                            "labels": meal.recipe.Labels
                        })

                    }
                })
        }
    }
})