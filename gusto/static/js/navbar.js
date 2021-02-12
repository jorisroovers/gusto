

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
