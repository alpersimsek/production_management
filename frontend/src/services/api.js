import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export const authAPI = {
  async login (email, password) {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  async logout () {
    const response = await api.post('/auth/logout')
    return response.data
  },

  async getCurrentUser () {
    const response = await api.get('/auth/me')
    return response.data
  },

  async refreshToken (refreshToken) {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  }
}

export const ordersAPI = {
  async getOrders (params = {}) {
    const response = await api.get('/orders/', { params })
    return response.data
  },

  async getOrder (orderId) {
    const response = await api.get(`/orders/${orderId}`)
    return response.data
  },

  async createOrder (orderData) {
    const response = await api.post('/orders/', orderData)
    return response.data
  },

  async updateOrder (orderId, orderData) {
    const response = await api.put(`/orders/${orderId}`, orderData)
    return response.data
  },

  async deleteOrder (orderId) {
    const response = await api.delete(`/orders/${orderId}`)
    return response.data
  },

  async getOrderItems (orderId) {
    const response = await api.get(`/orders/${orderId}/items`)
    return response.data
  },

  async createOrderItem (orderId, itemData) {
    const response = await api.post(`/orders/${orderId}/items`, itemData)
    return response.data
  },

  async updateOrderItem (itemId, itemData) {
    const response = await api.put(`/orders/items/${itemId}`, itemData)
    return response.data
  },

  async deleteOrderItem (itemId) {
    const response = await api.delete(`/orders/items/${itemId}`)
    return response.data
  }
}

export const customersAPI = {
  async getCustomers (params = {}) {
    const response = await api.get('/customers/', { params })
    return response.data
  },

  async getCustomer (customerId) {
    const response = await api.get(`/customers/${customerId}`)
    return response.data
  },

  async createCustomer (customerData) {
    const response = await api.post('/customers/', customerData)
    return response.data
  },

  async updateCustomer (customerId, customerData) {
    const response = await api.put(`/customers/${customerId}`, customerData)
    return response.data
  },

  async deleteCustomer (customerId) {
    const response = await api.delete(`/customers/${customerId}`)
    return response.data
  }
}

export const productsAPI = {
  async getProducts (params = {}) {
    const response = await api.get('/products/', { params })
    return response.data
  },

  async getProduct (productId) {
    const response = await api.get(`/products/${productId}`)
    return response.data
  },

  async createProduct (productData) {
    const response = await api.post('/products/', productData)
    return response.data
  },

  async updateProduct (productId, productData) {
    const response = await api.put(`/products/${productId}`, productData)
    return response.data
  },

  async deleteProduct (productId) {
    const response = await api.delete(`/products/${productId}`)
    return response.data
  }
}

export default api
