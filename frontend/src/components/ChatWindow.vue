<script setup>
import { ref, defineProps, defineEmits, nextTick } from 'vue'
import ChartDisplay from './ChartDisplay.vue'

const props = defineProps({
  messages: { type: Array, required: true },
  isLoading: { type: Boolean, required: true }
})

const emit = defineEmits(['sendMessage', 'confirmChart'])

// Local state for the input field
const localInput = ref('')
const messagesContainer = ref(null) // Reference to the scrollable div

// Scrolls the messages container to the bottom when a new message arrives
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Watch the messages array for changes to trigger the scroll
// (Note: This is a sophisticated Vue concept, but essential for chat UI)
import { watch } from 'vue'
watch(
  () => props.messages.length,
  () => {
    scrollToBottom()
  }
)

const handleSend = () => {
  // Pass the prompt up to the App.vue logic
  emit('sendMessage', localInput.value)
  localInput.value = '' 
}

const handleConfirm = (jobId) => {
    emit('confirmChart', jobId)
}
</script>

<template>
  <div class="chat-window">
    
    <div class="chat-header">
      <span>DataChat Assistant</span>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="(msg, index) in props.messages" 
        :key="index" 
        :class="['message', msg.sender]"
      >
        <p>{{ msg.text }}</p>
        
        <ChartDisplay 
            v-if="msg.type === 'preview'" 
            :chart-url="msg.chartUrl"
            :preview-data="msg.previewData"
            @confirm="handleConfirm"
        />
      </div>
      
      <div v-if="props.isLoading" class="loading">
        <p>Thinking...</p>
      </div>
    </div>

    <div class="chat-input">
      <input 
        v-model="localInput" 
        placeholder="Ask for a graph or data summary..." 
        @keyup.enter="handleSend"
        :disabled="props.isLoading"
      />
      <button @click="handleSend" :disabled="props.isLoading">Send</button>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 380px;
  height: 550px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 999;
}

.chat-header {
  padding: 10px;
  background: #f4f4f4;
  border-bottom: 1px solid #ddd;
  text-align: center;
  font-weight: bold;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 15px;
  font-size: 14px;
}

.message.user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
}

.message.bot {
  align-self: flex-start;
  background-color: #e9ecef;
  color: black;
}

.loading {
    padding: 5px 10px;
    background: #f1f1f1;
    border-radius: 5px;
    align-self: flex-start;
    font-style: italic;
    font-size: 0.9em;
}

.chat-input {
  padding: 10px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 5px;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>