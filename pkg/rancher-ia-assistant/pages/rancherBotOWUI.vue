<template>
  <div class="chatbot-container" v-if="owiurl">
    <iframe class="owui" :src="owiurl" />
  </div>
</template>

<script>
export default {
  name: 'rancherBotOWUI',

  data() {
    return {
      owiurl: this.$store.getters['rancher-ai-assistant/ollamaUrl'],
    };
  },

  computed: {
  },

  mounted() {    
  },

  methods: {
  }
};
</script>

<style scoped>
.owui {
  width: 100%;
  height: 90vh;
  border: none;
  background: transparent;
}
</style>
