<template>
  <div class="chat-window">
    <div class="messages-container" ref="chatBox">
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        <p v-if="msg.content">{{ msg.content }}</p>

        <div v-if="msg.chartUrl" class="chart-result">
          <img :src="'http://localhost:8000' + msg.chartUrl" alt="Generated Data Insight" />
        </div>

        <div v-if="msg.showConfirm" class="preview-card">
          <pre><code>{{ msg.sql }}</code></pre>
          <button @click="confirmAndExecute(msg.jobId)">✅ Execute Full Chart</button>
        </div>
      </div>
    </div>

    <div class="input-area">
      <input v-model="userInput" @keyup.enter="handleSend" placeholder="Ask about sales..." />
      <button @click="handleSend">Send</button>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      userInput: '',
      messages: [],
      loading: false
    };
  },
  methods: {
    async handleSend() {
      if (!this.userInput.trim()) return;

      const userText = this.userInput;
      this.messages.push({ role: 'user', content: userText });
      this.userInput = '';

      try {
        // Phase 1: Analyze
        const data = await api.analyzePrompt(userText);
        
        this.messages.push({
          role: 'bot',
          content: 'Here is the generated SQL preview. Should I plot the full chart?',
          sql: data.generated_sql,
          jobId: data.job_id,
          showConfirm: true
        });
      } catch (err) {
        this.messages.push({ role: 'bot', content: 'Error analyzing query. Check your DB connection.' });
      }
    },

    async confirmAndExecute(jobId) {
      try {
        // Phase 2: Execute
        const result = await api.executeChart(jobId);
        
        // Remove the button from the last message
        const lastMsg = this.messages[this.messages.length - 1];
        lastMsg.showConfirm = false;

        // Add new message with the chart URL
        this.messages.push({
          role: 'bot',
          content: `Chart generated successfully! Rows processed: ${result.data_summary.total_rows}`,
          chartUrl: result.chart_url
        });
      } catch (err) {
        alert("Execution failed. Session might have expired.");
      }
    }
  }
};
</script>

<style scoped>
.message.bot { background: #f1f1f1; border-radius: 8px; padding: 10px; margin: 5px; }
.message.user { background: #007bff; color: white; align-self: flex-end; padding: 10px; border-radius: 8px; margin: 5px; }
.preview-card { border: 1px solid #ccc; padding: 10px; margin-top: 10px; background: #fffde7; }
.chart-result img { max-width: 100%; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
</style>