<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios' // We will need this later
import FloatingButton from './components/FloatingButton.vue'
import ChatWindow from './components/ChatWindow.vue'

// --- 1. CORE STATE MANAGEMENT ---
// Using ref() for simple primitives and reactive() for complex objects if needed.
const isChatOpen = ref(false)
const userInput = ref('')
const isLoading = ref(false)

// Messages state: array of objects to store history
const messages = ref([
  { sender: 'bot', text: 'Hello! Ask me to generate a dashboard or chart.', type: 'text' }
])

// --- 2. ACTIONS/METHODS ---

// Toggles the visibility of the chat window
const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
}

// MOCK FUNCTION: Simulates sending and receiving a message
const sendMessage = async (prompt) => {
  if (!prompt.trim() || isLoading.value) return
  
  // 1. Add user message
  messages.value.push({ sender: 'user', text: prompt, type: 'text' })
  userInput.value = ''
  isLoading.value = true

  try {
    // --- MOCK API CALL (To be replaced in the Backend Phase) ---
    await new Promise(r => setTimeout(r, 2000)) 
    // MOCK Response structure (Preview or Result)
    
    // MOCK: Simulate chart result
    const mockChartUrl = 'https://via.placeholder.com/400x250?text=Mock+Chart+ID' + Math.floor(Math.random() * 100)
    messages.value.push({ 
      sender: 'bot', 
      text: 'Plan generated. Click here to confirm execution or view the preview below.', 
      type: 'preview',
      previewData: { sql: 'SELECT * FROM sales LIMIT 5', rows: 5 },
      chartUrl: mockChartUrl // We use this for display
    })

  } catch (error) {
    messages.value.push({ sender: 'bot', text: 'Connection error.', type: 'text' })
  } finally {
    isLoading.value = false
  }
}

// Handler for the chart confirmation button (currently mocks full execution)
const handleConfirmation = (jobId) => {
    // Logic will run the full API /execute endpoint (in future phase)
    messages.value.push({ 
        sender: 'bot', 
        text: `Executing job ${jobId}. Result below...`,
        type: 'text'
    })
}

</script>

<template>
  <div class="app-container">
    <FloatingButton @toggle="toggleChat" />

    <ChatWindow 
      v-if="isChatOpen"
      :messages="messages"
      :is-loading="isLoading"
      @send-message="sendMessage"
      @confirm-chart="handleConfirmation"
    />
  </div>
</template>

<style>
/* Global CSS for the application container */
body { margin: 0; background-color: #f8f9fa; }
</style>