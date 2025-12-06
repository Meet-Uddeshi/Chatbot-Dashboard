<script setup>
// Define events this component can send to its parent
const emit = defineEmits(['toggle']) 
</script>

<template>
  <button class="toggle-btn" @click="emit('toggle')">
    💬
  </button>
</template>

<style scoped>
.toggle-btn {
  /* Positioning is critical for the "Floating" requirement */
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  z-index: 1000; /* Ensure it stays above other elements */
}
</style>