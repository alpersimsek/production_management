import axios from 'axios'

const endpoints = {
  auth: {
    login: '/login',
  },
  users: {
    list: '/users',
    create: '/users',
    update: (userId) => `/users/${userId}`,
    delete: (userId) => `/users/${userId}`,
  },
  files: {
    list: '/files',
    upload: '/files/upload',
    process: (fileId) => `/files/process/${fileId}`,
    delete: (fileId) => `/files/delete/${fileId}`,
    download: (fileId) => `/files/download/${fileId}`,
  },
  maskingMaps: {
    search: '/masking/search',
    categories: '/masking/categories',
    export: '/masking/export',
  },
  presets: {
    list: '/presets',
    get: (presetId) => `/presets/${presetId}`,
    create: '/presets',
    update: (presetId) => `/presets/${presetId}`,
    delete: (presetId) => `/presets/${presetId}`,
    rules: (presetId) => `/presets/${presetId}/rules`,
  },
  products: {
    list: '/products',
  },
  rules: {
    list: '/rules',
    get: (ruleId) => `/rules/${ruleId}`,
    create: '/rules',
    update: (ruleId) => `/rules/${ruleId}`,
    delete: (ruleId) => `/rules/${ruleId}`,
  },
  presetRules: {
    create: '/preset-rules',
    update: (presetId, ruleId) => `/preset-rules/${presetId}/${ruleId}`,
    delete: (presetId, ruleId) => `/preset-rules/${presetId}/${ruleId}`,
  },
}

class ApiError extends Error {
  constructor(status, message, data = null) {
    super(message)
    this.status = status
    this.data = data
  }
}

const handleApiError = (error) => {
  if (error.response) {
    // Handle specific error cases
    switch (error.response.status) {
      case 401:
        throw new ApiError(401, 'Invalid credentials')
      case 403:
        throw new ApiError(403, 'Access denied')
      case 404:
        throw new ApiError(404, 'Resource not found')
      default:
        throw new ApiError(
          error.response.status,
          error.response.data?.detail || 'An error occurred',
          error.response.data,
        )
    }
  } else if (error.request) {
    throw new ApiError(503, 'Service unavailable')
  } else {
    throw new ApiError(500, error.message || 'An unexpected error occurred')
  }
}

class ApiService {
  // Auth
  static async login(credentials) {
    try {
      const response = await axios.post(endpoints.auth.login, credentials)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  // User management
  static async getUsers() {
    try {
      const response = await axios.get(endpoints.users.list)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async createUser(userData) {
    try {
      const response = await axios.post(endpoints.users.create, userData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async updateUserPassword(userId, passwordData) {
    try {
      const response = await axios.put(endpoints.users.update(userId), passwordData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async deleteUser(userId) {
    try {
      const response = await axios.delete(endpoints.users.delete(userId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  // File management
  static async getFiles() {
    try {
      // console.log('Files endpoint:', endpoints.files.list);
      // console.log('Base URL:', axios.defaults.baseURL);
      const response = await axios.get(endpoints.files.list)
      // console.log('Raw /files response:', response)
      // console.log('Files data:', response.data)
      return response.data
    } catch (error) {
      console.error('Error in getFiles:', error)
      handleApiError(error)
    }
  }

  static async uploadFile(file) {
    try {
      // Add initial validation
      if (!file || !(file instanceof File)) {
        throw new ApiError(400, 'Invalid file object')
      }

      // Check file size - assuming a 100MB limit
      const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB
      if (file.size > MAX_FILE_SIZE) {
        throw new ApiError(413, `File size exceeds the maximum allowed (${Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB)`)
      }

      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await axios.post(endpoints.files.upload, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const progress = {
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percent: Math.round((progressEvent.loaded * 100) / progressEvent.total),
            }
            window.dispatchEvent(
              new CustomEvent('file-upload-progress', {
                detail: { fileId: file.name, progress },
              }),
            )
          },
          // Add timeout to prevent hanging uploads
          timeout: 60000, // 60 seconds
        })
        return response.data
      } catch (axiosError) {
        // Handle specific upload errors
        if (axiosError.code === 'ECONNABORTED') {
          throw new ApiError(408, 'Upload timed out. Please try again.')
        }

        if (axiosError.response?.status === 413) {
          throw new ApiError(413, 'File size exceeds server limit')
        }

        handleApiError(axiosError)
      }
    } catch (error) {
      // If it's already an ApiError, just rethrow it
      if (error instanceof ApiError) {
        throw error
      }
      // Otherwise create a generic error
      throw new ApiError(500, error.message || 'File upload failed')
    }
  }

  static async processFile(fileId) {
    try {
      // console.log(`Making POST request to process file ${fileId}`)
      // Add timeout to prevent blocking
      const response = await axios.post(endpoints.files.process(fileId), null, {
        timeout: 2000, // 2 second timeout
      })
      console.log('Process response:', response.data)
      return response.data
    } catch (error) {
      // If it's a timeout error, we can ignore it as the process is likely still running
      if (error.code === 'ECONNABORTED') {
        console.log('Process request timed out (expected, processing continues in background)')
        return { status: 'in-progress' }
      }
      console.error('Error in processFile:', error)
      handleApiError(error)
    }
  }

  static async deleteFile(fileId) {
    try {
      const response = await axios.delete(endpoints.files.delete(fileId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async downloadFile(fileId) {
    try {
      // First, request a signed URL from the server
      const response = await axios({
        url: `/files/get_download_url/${fileId}`,
        method: 'GET'
      })

      if (!response.data || !response.data.signedUrl) {
        throw new Error('Failed to get download URL')
      }

      // The signed URL includes authentication information
      // and will be valid for a limited time (e.g., 5 minutes)
      const signedUrl = response.data.signedUrl

      // Using window.open or location.href directly will trigger the immediate save dialog
      // as the browser navigates to the signed URL
      // window.open(signedUrl, '_blank')
      window.location.href = signedUrl

      return true
    } catch (error) {
      console.error('Download failed:', error)
      handleApiError(error)
      throw error
    }
  }

  // GDPR Masking Maps
  static async getMaskingCategories() {
    try {
      const response = await axios.get(endpoints.maskingMaps.categories)

      // Validate response format
      if (!Array.isArray(response.data)) {
        console.warn('Unexpected response format from masking categories endpoint:', response.data)
        return []
      }

      return response.data
    } catch (error) {
      console.error('Failed to fetch masking categories:', error)
      handleApiError(error)
    }
  }

  static async searchMaskingMaps(params) {
    try {
      // Add validation for params
      const validatedParams = {
        ...params
      }

      // Ensure categories is an array if provided
      if (validatedParams.categories && !Array.isArray(validatedParams.categories)) {
        validatedParams.categories = [validatedParams.categories]
      }

      const response = await axios.get(endpoints.maskingMaps.search, {
        params: validatedParams
      })

      // Validate response format
      if (!Array.isArray(response.data)) {
        console.warn('Unexpected response format from masking search endpoint:', response.data)
        return []
      }

      return response.data
    } catch (error) {
      console.error('Failed to search masking maps:', error)
      handleApiError(error)
    }
  }

  static async exportMaskingMaps(params) {
    try {
      // Add validation for params
      const validatedParams = {
        ...params
      }

      // Ensure categories is an array if provided
      if (validatedParams.categories && !Array.isArray(validatedParams.categories)) {
        validatedParams.categories = [validatedParams.categories]
      }

      const response = await axios.get(endpoints.maskingMaps.export, {
        params: validatedParams,
        responseType: 'blob'
      })

      // Validate response is a blob
      if (!(response.data instanceof Blob)) {
        throw new Error('Export response is not a valid file')
      }

      return response.data
    } catch (error) {
      console.error('Failed to export masking maps:', error)
      handleApiError(error)
    }
  }

  // Product and Preset Management
  static async getProducts() {
    try {
      const response = await axios.get(endpoints.products.list)
      return response.data
    } catch (error) {
      console.error('Failed to fetch products:', error)
      handleApiError(error)
    }
  }

  static async getPresets() {
    try {
      const response = await axios.get(endpoints.presets.list)
      return response.data
    } catch (error) {
      console.error('Failed to fetch presets:', error)
      handleApiError(error)
    }
  }

  static async getPreset(presetId) {
    try {
      const response = await axios.get(endpoints.presets.get(presetId))
      return response.data
    } catch (error) {
      console.error(`Failed to fetch preset ${presetId}:`, error)
      handleApiError(error)
    }
  }

  static async createPreset(presetData) {
    try {
      const response = await axios.post(endpoints.presets.create, presetData)
      return response.data
    } catch (error) {
      console.error('Failed to create preset:', error)
      handleApiError(error)
    }
  }

  static async updatePreset(presetId, presetData) {
    try {
      const response = await axios.put(endpoints.presets.update(presetId), presetData)
      return response.data
    } catch (error) {
      console.error(`Failed to update preset ${presetId}:`, error)
      handleApiError(error)
    }
  }

  static async deletePreset(presetId) {
    try {
      const response = await axios.delete(endpoints.presets.delete(presetId))
      return response.data
    } catch (error) {
      console.error(`Failed to delete preset ${presetId}:`, error)
      handleApiError(error)
    }
  }

  // Rules Management
  static async getRules() {
    try {
      const response = await axios.get(endpoints.rules.list)
      return response.data
    } catch (error) {
      console.error('Failed to fetch rules:', error)
      handleApiError(error)
    }
  }

  static async getRule(ruleId) {
    try {
      const response = await axios.get(endpoints.rules.get(ruleId))
      return response.data
    } catch (error) {
      console.error(`Failed to fetch rule ${ruleId}:`, error)
      handleApiError(error)
    }
  }

  static async createRule(ruleData) {
    try {
      const response = await axios.post(endpoints.rules.create, ruleData)
      return response.data
    } catch (error) {
      console.error('Failed to create rule:', error)
      handleApiError(error)
    }
  }

  static async updateRule(ruleId, ruleData) {
    try {
      const response = await axios.put(endpoints.rules.update(ruleId), ruleData)
      return response.data
    } catch (error) {
      console.error(`Failed to update rule ${ruleId}:`, error)
      handleApiError(error)
    }
  }

  static async deleteRule(ruleId) {
    try {
      const response = await axios.delete(endpoints.rules.delete(ruleId))
      return response.data
    } catch (error) {
      console.error(`Failed to delete rule ${ruleId}:`, error)
      handleApiError(error)
    }
  }

  static async getPresetRules(presetId) {
    try {
      const response = await axios.get(endpoints.presets.rules(presetId))
      return response.data
    } catch (error) {
      console.error(`Failed to fetch rules for preset ${presetId}:`, error)
      handleApiError(error)
    }
  }

  static async createPresetRule(ruleData) {
    try {
      const response = await axios.post(endpoints.presetRules.create, ruleData)
      return response.data
    } catch (error) {
      console.error('Failed to create preset rule:', error)
      handleApiError(error)
    }
  }

  static async updatePresetRule(presetId, ruleId, ruleData) {
    try {
      const response = await axios.put(
        endpoints.presetRules.update(presetId, ruleId),
        ruleData
      )
      return response.data
    } catch (error) {
      console.error(`Failed to update rule ${ruleId} for preset ${presetId}:`, error)
      handleApiError(error)
    }
  }

  static async deletePresetRule(presetId, ruleId) {
    try {
      const response = await axios.delete(endpoints.presetRules.delete(presetId, ruleId))
      return response.data
    } catch (error) {
      console.error(`Failed to delete rule ${ruleId} for preset ${presetId}:`, error)
      handleApiError(error)
    }
  }
}

export default ApiService
