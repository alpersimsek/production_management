// src/utils/constants.ts
export const FILE_SIZE_LIMIT = 2 * 1024 * 1024 * 1024; // 2GB
export const CHUNK_SIZE = 1024 * 1024; // 1MB
export const ALLOWED_FILE_TYPES = [
  'application/zip',
  'application/x-tar',
  'application/gzip',
  'text/plain',
  'text/csv',
  'application/vnd.tcpdump.pcap',
  'application/x-compressed',
  'application/x-gzip',
  'application/x-zip-compressed'
];

export const FOLDER_TYPES = {
  UPLOADS: 'uploads',
  PROCESSED: 'processed',
  PROCESSED_ZIP: 'processed_zip'
} as const;

export const formatBytes = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
};

export const formatProgress = (progress: number): string => {
  return `${Math.round(progress)}%`;
};

export const validateFile = (file: File): string | null => {
  console.log(`fileSize: ${file.size}, fileType: ${file.type}`)
  if (file.size > FILE_SIZE_LIMIT) {
    return `File size exceeds ${formatBytes(FILE_SIZE_LIMIT)}`;
  }
  
  if (!ALLOWED_FILE_TYPES.includes(file.type)) {
    return 'File type not supported';
  }
  
  return null;
};

export const validatePassword = (password: string): string | null => {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number';
  }
  return null;
};