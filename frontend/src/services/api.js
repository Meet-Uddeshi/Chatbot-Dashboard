import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export default {
  async analyzePrompt(prompt) {
    try {
      const response = await axios.post(`${API_URL}/analyze`, {
        prompt: prompt,
        // CRITICAL UPDATE: Point to your actual table 'sales_data'
        context_tables: ["sales_data"] 
      });
      return response.data; // Returns { job_id, generated_sql, preview_rows, ... }
    } catch (error) {
      console.error("API Analyze Error:", error);
      throw error;
    }
  },

  async executeChart(jobId) {
    try {
      const response = await axios.post(`${API_URL}/execute`, {
        job_id: jobId
      });
      return response.data; // Returns { status, chart_url, data_summary }
    } catch (error) {
      console.error("API Execute Error:", error);
      throw error;
    }
  }
};