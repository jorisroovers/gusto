Vue.component('recipe-tag', {
    props: ['tag'],
    template: `
    <span class="tag" :data-value="tag.name">
        {{tag.display_name}}
    </span>
    `
})