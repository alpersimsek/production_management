import axios, { AxiosError } from 'axios';
import { toast } from 'react-toastify';
import type {
  LoginRequest,
  LoginResponse,
  User,
  CreateUserRequest,
  FileUploadChunk,
  ProcessingResponse,
  ProcessingProgress,
  FileListResponse,
  FolderType,
} from '../types/api';

// Base configuration for API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Configured axios instance with base URL and default headers
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor that adds authentication token to all requests
 * Token is retrieved from localStorage
 */
api.interceptors.request.use((config) => {
  console.log(`Request: ${config.method} ${config.url}`);
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Response interceptor for centralized error handling
 * Logs responses and errors, forwards to error handler
 */
api.interceptors.response.use(
  (response) => {
    console.log(`Response: ${response.status} ${response.statusText}`);
    return response;
  },
  (error) => {
    console.log(`Error: ${error.message}`);
    handleApiError(error);
    return Promise.reject(error);
  }
);

/**
 * Authentication service for user login
 */
export const authService = {
  /**
   * Authenticates user and returns access token
   * @param credentials - User login credentials
   * @returns Promise with login response containing access token and user role
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      console.log(`Login response: ${JSON.stringify(response.data)}`);
      toast.success('Login successful');
      return response.data;
    } catch (error) {
      toast.error('Login failed');
      throw error;
    }
  },
};

/**
 * User management service for admin operations
 */
export const userService = {
  /**
   * Creates a new user account (Admin only)
   * @param userData - New user details including username, password, and role
   * @returns Promise with created user data
   */
  createUser: async (userData: CreateUserRequest): Promise<User> => {
    try {
      const response = await api.post<User>('/admin/create_user', userData);
      console.log(`Create user response: ${JSON.stringify(response.data)}`);
      toast.success('User created successfully');
      return response.data;
    } catch (error) {
      toast.error('Failed to create user');
      throw error;
    }
  },

  /**
   * Lists all non-admin users (Admin only)
   * @returns Promise with array of user objects
   */
  listUsers: async (): Promise<User[]> => {
    try {
      const response = await api.get<User[]>('/admin/list_users');
      console.log(`List users response: ${JSON.stringify(response.data)}`);
      return response.data;
    } catch (error) {
      toast.error('Failed to list users');
      throw error;
    }
  },

  /**
   * Updates user password (Admin only)
   * @param username - Target user's username
   * @param password - New password
   */
  updatePassword: async (username: string, password: string): Promise<void> => {
    try {
      await api.put(`/admin/update_password/${username}`, { password });
      console.log(`Password update response: success`);
      toast.success('Password updated successfully');
    } catch (error) {
      toast.error('Failed to update password');
      throw error;
    }
  },

  /**
   * Deletes user account (Admin only)
   * @param username - Username of account to delete
   */
  deleteUser: async (username: string): Promise<void> => {
    try {
      await api.delete(`/admin/delete_user/${username}`);
      console.log(`Delete user response: success`);
      toast.success('User deleted successfully');
    } catch (error) {
      toast.error('Failed to delete user');
      throw error;
    }
  },
};

/**
 * File processing service for handling file operations
 */
export const fileService = {
  /**
   * Uploads file with optional chunking support
   * @param data - File upload data including file, username, and optional chunking info
   */
  uploadFile: async (data: FileUploadChunk): Promise<void> => {
    try {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('username', data.username);
      
      // Add chunking information if present
      if (data.chunk_index !== undefined) {
        formData.append('chunk_index', data.chunk_index.toString());
        formData.append('total_chunks', data.total_chunks?.toString() ?? '');
        formData.append('file_size', data.file_size?.toString() ?? '');
      }

      const response = await api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(`Upload file response: ${JSON.stringify(response.data)}`);
      toast.success('File uploaded successfully');
    } catch (error) {
      toast.error('Failed to upload file');
      throw error;
    }
  },

  /**
   * Initiates file processing
   * @param filename - Name of file to process
   * @param username - Owner of the file
   * @returns Promise with processing task details
   */
  processFile: async (filename: string, username: string): Promise<ProcessingResponse> => {
    try {
      const response = await api.post<ProcessingResponse>(
        `/files/process/${encodeURIComponent(filename)}`,
        { username }
      );
      console.log(`Process file response: ${JSON.stringify(response.data)}`);
      toast.success('File processing started');
      return response.data;
    } catch (error) {
      toast.error('Failed to start file processing');
      throw error;
    }
  },

  /**
   * Checks file processing progress
   * @param taskId - ID of processing task
   * @returns Promise with progress information
   */
  checkProcessingProgress: async (taskId: string): Promise<ProcessingProgress> => {
    try {
      const response = await api.get<ProcessingProgress>(`/files/process/progress/${taskId}`);
      console.log(`Check processing progress response: ${JSON.stringify(response.data)}`);
      return response.data;
    } catch (error) {
      toast.error('Failed to check processing progress');
      throw error;
    }
  },

  /**
   * Initiates PII masking process
   * @param filename - Name of file to mask
   * @param username - Owner of the file
   * @returns Promise with masking task details
   */
  maskFile: async (filename: string, username: string): Promise<ProcessingResponse> => {
    try {
      console.log(`Masking file: ${filename}`);
      const response = await api.post<ProcessingResponse>(
        `/files/mask/${encodeURIComponent(filename)}`,
        { username }
      );
      console.log(`Mask file response: ${JSON.stringify(response.data)}`);
      toast.success('File masking started');
      return response.data;
    } catch (error) {
      toast.error('Failed to start file masking');
      throw error;
    }
  },

  /**
   * Checks PII masking progress
   * @param taskId - ID of masking task
   * @returns Promise with progress information
   */
  checkMaskingProgress: async (taskId: string): Promise<ProcessingProgress> => {
    try {
      const response = await api.get<ProcessingProgress>(`/files/masking/progress/${taskId}`);
      console.log(`Check masking progress response: ${JSON.stringify(response.data)}`);
      return response.data;
    } catch (error) {
      toast.error('Failed to check masking progress');
      throw error;
    }
  },

  /**
   * Creates final masked archive
   * @param filename - Name of file to archive
   * @param username - Owner of the file
   * @returns Promise with archive task details
   */
  createFinalArchive: async (filename: string, username: string): Promise<ProcessingResponse> => {
    try {
      console.log(`Creating final archive for file: ${filename}`);
      const response = await api.post<ProcessingResponse>(
        `/files/zipMask/${encodeURIComponent(filename)}`,
        { username }
      );
      console.log(`Create final archive response: ${JSON.stringify(response.data)}`);
      toast.success('Final archive creation started');
      return response.data;
    } catch (error) {
      toast.error('Failed to start archive creation');
      throw error;
    }
  },

  /**
   * Checks archive creation progress
   * @param taskId - ID of archive task
   * @returns Promise with progress information
   */
  checkArchiveProgress: async (taskId: string): Promise<ProcessingProgress> => {
    try {
      console.log(`Checking archive progress for task ID: ${taskId}`);
      const response = await api.get<ProcessingProgress>(`/files/masking/zip/${taskId}`);
      console.log(`Check archive progress response: ${JSON.stringify(response.data)}`);
      return response.data;
    } catch (error) {
      toast.error('Failed to check archive progress');
      throw error;
    }
  },

  /**
   * Lists files in specified folder
   * @param username - Owner of the files
   * @param folder - Folder type (uploads, processed, processed_zip)
   * @returns Promise with list of files
   */
  listFiles: async (username: string, folder: FolderType): Promise<FileListResponse> => {
    try {
      const response = await api.get<FileListResponse>(`/files/${username}/${folder}`);
      console.log(`List files response: ${JSON.stringify(response.data)}`);
      return response.data;
    } catch (error) {
      toast.error('Failed to list files');
      throw error;
    }
  },

  /**
   * Downloads specified file
   * @param username - Owner of the file
   * @param filename - Name of file to download
   * @returns Promise with file blob
   */
  downloadFile: async (username: string, filename: string): Promise<Blob> => {
    try {
      const response = await api.get(`/files/download/${username}/${encodeURIComponent(filename)}`, {
        responseType: 'blob',
      });
      console.log(`Download file response: ${response.headers['content-disposition']}`);
      toast.success('File downloaded successfully');
      return response.data;
    } catch (error) {
      toast.error('Failed to download file');
      throw error;
    }
  },

  /**
   * Deletes specified file
   * @param username - Owner of the file
   * @param folder - Folder containing the file
   * @param filename - Name of file to delete
   */
  deleteFile: async (username: string, folder: FolderType, filename: string): Promise<void> => {
    try {
      await api.delete(`/files/delete/${username}/${folder}/${encodeURIComponent(filename)}`);
      console.log(`Delete file response: success`);
      toast.success('File deleted successfully');
    } catch (error) {
      toast.error('Failed to delete file');
      throw error;
    }
  },

  /**
   * Downloads GDPR mapping file
   * @returns Promise with GDPR map blob
   */
  getGdprMap: async (): Promise<Blob> => {
    try {
      const response = await api.get('/files/gdpr_map', {
        responseType: 'blob',
      });
      console.log(`Get GDPR map response: ${response.headers['content-disposition']}`);
      console.log(response.data)
      return response.data;
    } catch (error) {
      toast.error('Failed to get GDPR map');
      throw error;
    }
  },
};

/**
 * Handles API errors, including authentication failures
 * Redirects to login page on 401 responses
 * @param error - Error object from API call
 */
export const handleApiError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    if (axiosError.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    throw new Error(axiosError.response?.data?.detail || axiosError.message);
  }
  throw error;
};