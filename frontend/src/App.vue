<script setup>
import { ref, watch } from 'vue'
import axios from 'axios' 
import FloatingButton from './components/FloatingButton.vue'
import ChatWindow from './components/ChatWindow.vue'

// --- CORE STATE MANAGEMENT ---
const API_BASE_URL = 'http://localhost:8000/api/v1' // CRITICAL: Link to FastAPI
const isChatOpen = ref(false)
const isLoading = ref(false)
const jobCache = ref({}) // Stores the generated SQL/VizSpec by job_id

const messages = ref([
  { sender: 'bot', text: 'Hello! Ask me for charts on sales or user data.', type: 'text' }
])

// --- ACTIONS/METHODS ---

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
}

// Phase 1: NL Submission -> SQL Preview
const sendMessage = async (prompt) => {
  if (!prompt.trim() || isLoading.value) return
  
  messages.value.push({ sender: 'user', text: prompt, type: 'text' })
  isLoading.value = true

  try {
    const payload = { 
        prompt: prompt, 
        context_tables: ["sales", "products", "users"] // Explicit table context for LLM
    }
    
    // POST /analyze
    const response = await axios.post(`${API_BASE_URL}/analyze`, payload)
    const data = response.data

    if (data.needs_clarification) {
        messages.value.push({ sender: 'bot', text: data.missing_info_question, type: 'text' })
    } else {
        // Cache the full response for Phase 2 execution
        jobCache.value[data.job_id] = data
        
        const previewText = `SQL generated. Check the preview below before executing the full query (Job ID: ${data.job_id}):`
        
        messages.value.push({ 
            sender: 'bot', 
            text: previewText,
            type: 'preview',
            previewData: { 
                sql: data.generated_sql, 
                rows: data.preview_rows.length 
            },
            jobId: data.job_id
            // No chartUrl yet, chartUrl comes after /execute
        })
    }
  } catch (error) {
    const errorDetail = error.response?.data?.detail || 'Server error or invalid query generated.'
    messages.value.push({ sender: 'bot', text: `Error: ${errorDetail}`, type: 'text' })
  } finally {
    isLoading.value = false
  }
}

// Phase 2: Confirmation -> Full Query Execution
const handleConfirmation = async (jobId) => {
    if (isLoading.value) return

    messages.value.push({ sender: 'bot', text: `Executing full query for Job ${jobId}...`, type: 'text' })
    isLoading.value = true
    
    try {
        // POST /execute
        const response = await axios.post(`${API_BASE_URL}/execute`, { job_id: jobId, confirmed: true })
        const data = response.data

        if (data.status === 'completed' && data.chart_url) {
            messages.value.push({ 
                sender: 'bot', 
                text: `Chart completed successfully. Total rows processed: ${data.data_summary.total_rows}.`, 
                type: 'result',
                chartUrl: `http://localhost:8000${data.chart_url}` // CRITICAL: prepend base URL for serving
            })
        }
    } catch (error) {
        const errorDetail = error.response?.data?.detail || 'Failed to execute the query/render chart.'
        messages.value.push({ sender: 'bot', text: `Execution Error: ${errorDetail}`, type: 'text' })
    } finally {
        isLoading.value = false
    }
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
      @close-chat="toggleChat"
    />
  </div>
</template>

<style>
/* Global styles for the floating element positioning */
body { margin: 0; }
</style>