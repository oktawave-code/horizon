<template>
  <div class="uk-container uk-margin-top">
    <div class="uk-flex-middle" uk-grid>
      <div class="uk-width-4-5@m">
          <h3>Error occured</h3>
          <p>{{ $route.params.message || 'Application crashed with unknown reason. Please try again.' }}</p>
          <button class="uk-button uk-button-link" v-on:click="returnToHome">Return to home.</button>
      </div>
      <div class="uk-width-1-5@m uk-flex-first uk-text-right">
          <span uk-icon="icon: warning; ratio: 3"></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    returnToHome () {
      this.$router.push({ name: 'home' })
    }
  }
}
</script>
