<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  // The actual image URL (PNG path from FastAPI)
  chartUrl: { type: String, required: true },
  
  // Optional preview data returned by the /analyze endpoint
  previewData: { type: Object, default: null } 
})

const emit = defineEmits(['confirm'])

// Mock job ID for confirmation (in the real app, this comes from the /analyze response)
const mockJobId = 'job-' + Math.floor(Math.random() * 9999) 

const confirm = () => {
  emit('confirm', mockJobId)
}
</script>

<template>
  <div class="chart-display">
    
    <div v-if="props.previewData" class="preview-box">
        <p class="preview-header">🚨 **SQL Preview & Safety Check** 🚨</p>
        <div class="code-block">
            <p><strong>SQL:</strong> {{ props.previewData.sql.substring(0, 50) }}...</p>
            <p><strong>Sample Rows:</strong> {{ props.previewData.rows }}</p>
        </div>
        
        <button class="confirm-btn" @click="confirm">
            ✅ Execute Full Chart
        </button>
    </div>

    <img :src="props.chartUrl" alt="Generated Chart Preview" class="chart-img" />
  </div>
</template>

<style scoped>
.chart-display {
    padding: 10px 0;
    border-top: 1px dashed #ccc;
    margin-top: 10px;
}
.chart-img {
    width: 100%;
    height: auto;
    max-width: 100%;
    border-radius: 5px;
    margin-top: 10px;
}
.preview-box {
    border: 1px solid #ffc107;
    background-color: #fff3cd;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
.preview-header {
    font-weight: bold;
    color: #856404;
    margin-top: 0;
}
.code-block {
    background-color: #f7f7f7;
    padding: 8px;
    border-radius: 3px;
    font-size: 0.85em;
    font-family: monospace;
}
.confirm-btn {
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}
</style>