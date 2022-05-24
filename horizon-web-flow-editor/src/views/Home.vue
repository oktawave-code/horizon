<template>
  <div class="home" uk-height-viewport>
    <GraphsList/>
  </div>
</template>

<script>
import GraphsList from '@/components/GraphsList.vue'

export default {
  name: 'home',
  components: {
    GraphsList
  }
}
</script>
