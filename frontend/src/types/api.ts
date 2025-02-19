// Authentication Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: 'admin' | 'user';
  username: string;  // Adding the missing username field
}

// User Management Types
export interface User {
  username: string;
  role: 'admin' | 'user';
}

export interface CreateUserRequest {
  username: string;
  password: string;
  role: 'user';
}

// File Processing Types
export interface FileUploadChunk {
  file: File;
  username: string;
  chunk_index?: number;
  total_chunks?: number;
  file_size?: number;
}

export interface ProcessingResponse {
  detail: string;
  task_id: string;
  maskTask_id: string;
  zipMaskTask_id: string;
}

export interface ProcessingProgress {
  progress: number;
}

export interface FileListResponse {
  files: string[];
}

export type FolderType = 'uploads' | 'processed' | 'processed_zip';

// Error Response Type
export interface ErrorResponse {
  detail: string;
}
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: 'admin' | 'user';
}

export interface User {
  username: string;
  role: 'admin' | 'user';
}

export interface CreateUserRequest {
  username: string;
  password: string;
  role: 'user';
}

export interface GdprMapping {
  type: string;
  original: string;
  masked: string;
}

export interface GdprSearchResponse {
  mappings: GdprMapping[];
}