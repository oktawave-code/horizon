<template>
    <div>
        <ul class="uk-list">
            <li v-for="(err, index) in list" class="uk-text-danger uk-text-small" :key="index">{{err}}</li>
        </ul>
    </div>
</template>

<script>
export default {
  props: {
    list: Array
  }
}
</script>
