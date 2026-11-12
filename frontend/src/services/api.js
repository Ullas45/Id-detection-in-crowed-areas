import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 120000,
})

export async function checkHealth() {
  const { data } = await api.get('/health')
  return data
}

export async function processVideo(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/process-video', formData)
  return data
}

export async function processImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/detect/image', formData)
  return {
    ...data,
    output_url: new URL(data.output_image, apiBaseUrl).toString(),
  }
}
