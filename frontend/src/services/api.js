import axios from 'axios'

const endpoints = {
  auth: { login: '/login' },
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
    deleteAll: '/files/all_delete',
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
  products: { list: '/products' },
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
    switch (error.response.status) {
      case 401:
        throw new ApiError(401, 'Invalid credentials')
      case 403:
        throw new ApiError(403, 'Access denied')
      case 404:
        throw new ApiError(404, 'Resource not found')
      case 400:
        throw new ApiError(400, error.response.data?.detail || 'Invalid request')
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
  static async login(credentials) {
    try {
      const response = await axios.post(endpoints.auth.login, credentials)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

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

  static async getFiles() {
    try {
      const response = await axios.get(endpoints.files.list)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async uploadFile(file) {
    try {
      if (!file || !(file instanceof File)) {
        throw new ApiError(400, 'Invalid file object')
      }
      const MAX_FILE_SIZE = 10000 * 1024 * 1024
      if (file.size > MAX_FILE_SIZE) {
        throw new ApiError(413, `File size exceeds the maximum allowed (${Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB)`)
      }
      const formData = new FormData()
      formData.append('file', file)
      try {
        const response = await axios.post(endpoints.files.upload, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = {
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percent: Math.round((progressEvent.loaded * 100) / progressEvent.total),
            }
            window.dispatchEvent(
              new CustomEvent('file-upload-progress', { detail: { fileId: file.name, progress } })
            )
          },
          timeout: 0,
        })
        return response.data
      } catch (axiosError) {
        if (axiosError.code === 'ECONNABORTED') {
          throw new ApiError(408, 'Upload timed out. Please try again.')
        }   
        if (axiosError.response?.status === 413) {
          throw new ApiError(413, 'File size exceeds server limit')
        }
        handleApiError(axiosError)
      }
    } catch (error) {
      if (error instanceof ApiError) throw error
      throw new ApiError(500, error.message || 'File upload failed')
    }
  }

  static async processFile(fileId) {
    try {
      const response = await axios.post(endpoints.files.process(fileId), null, { timeout: 2000 })
      return response.data
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        return { status: 'in-progress' }
      }
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

  static async deleteAllFiles() {
    try {
      const response = await axios.delete(endpoints.files.deleteAll)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async downloadFile(fileId) {
    try {
      const response = await axios.get(`/files/get_download_url/${fileId}`)
      if (!response.data || !response.data.signedUrl) {
        throw new Error('Failed to get download URL')
      }
      window.location.href = response.data.signedUrl
      return true
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getMaskingCategories() {
    try {
      const response = await axios.get(endpoints.maskingMaps.categories)
      return Array.isArray(response.data) ? response.data : []
    } catch (error) {
      handleApiError(error)
    }
  }

  static async searchMaskingMaps(params) {
    try {
      const validatedParams = { ...params }
      if (validatedParams.categories && !Array.isArray(validatedParams.categories)) {
        validatedParams.categories = [validatedParams.categories]
      }
      const response = await axios.get(endpoints.maskingMaps.search, { params: validatedParams })
      return Array.isArray(response.data) ? response.data : []
    } catch (error) {
      handleApiError(error)
    }
  }

  static async exportMaskingMaps(params) {
    try {
      const validatedParams = { ...params }
      if (validatedParams.categories && !Array.isArray(validatedParams.categories)) {
        validatedParams.categories = [validatedParams.categories]
      }
      const response = await axios.get(endpoints.maskingMaps.export, {
        params: validatedParams,
        responseType: 'blob'
      })
      if (!(response.data instanceof Blob)) {
        throw new Error('Export response is not a valid file')
      }
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getProducts() {
    try {
      const response = await axios.get(endpoints.products.list)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getPresets() {
    try {
      const response = await axios.get(endpoints.presets.list)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getPreset(presetId) {
    try {
      const response = await axios.get(endpoints.presets.get(presetId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async createPreset(presetData) {
    try {
      const response = await axios.post(endpoints.presets.create, presetData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async updatePreset(presetId, presetData) {
    try {
      const response = await axios.put(endpoints.presets.update(presetId), presetData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async deletePreset(presetId) {
    try {
      const response = await axios.delete(endpoints.presets.delete(presetId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getRules(params = {}) {
    try {
      const response = await axios.get(endpoints.rules.list, { params })
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getRule(ruleId) {
    try {
      const response = await axios.get(endpoints.rules.get(ruleId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async createRule(ruleData) {
    try {
      const response = await axios.post(endpoints.rules.create, ruleData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async updateRule(ruleId, ruleData) {
    try {
      const response = await axios.put(endpoints.rules.update(ruleId), ruleData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async deleteRule(ruleId) {
    try {
      const response = await axios.delete(endpoints.rules.delete(ruleId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async getPresetRules(presetId) {
    try {
      const response = await axios.get(endpoints.presets.rules(presetId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async createPresetRule(ruleData) {
    try {
      const response = await axios.post(endpoints.presetRules.create, ruleData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async updatePresetRule(presetId, ruleId, ruleData) {
    try {
      const response = await axios.put(endpoints.presetRules.update(presetId, ruleId), ruleData)
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }

  static async deletePresetRule(presetId, ruleId) {
    try {
      const response = await axios.delete(endpoints.presetRules.delete(presetId, ruleId))
      return response.data
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default ApiService