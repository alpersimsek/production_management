import { useState, useCallback } from 'react';
import { fileService } from '../services/api';
import { CHUNK_SIZE, validateFile } from '../utils/constants';
import type { FileUploadChunk } from '../types/api';

interface UseFileUploadResult {
  uploadFile: (file: File, username: string) => Promise<void>;
  progress: number;
  isUploading: boolean;
  error: string | null;
}

export const useFileUpload = (): UseFileUploadResult => {
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = useCallback(async (file: File, username: string) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      if (file.size <= CHUNK_SIZE) {
        // Small file upload
        const data: FileUploadChunk = { file, username };
        await fileService.uploadFile(data);
        setProgress(100);
      } else {
        // Chunked upload for large files
        const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
        
        for (let chunk = 0; chunk < totalChunks; chunk++) {
          const start = chunk * CHUNK_SIZE;
          const end = Math.min(start + CHUNK_SIZE, file.size);
          const fileChunk = file.slice(start, end);
          
          const data: FileUploadChunk = {
            file: new File([fileChunk], file.name),
            username,
            chunk_index: chunk,
            total_chunks: totalChunks,
            file_size: file.size
          };

          await fileService.uploadFile(data);
          setProgress(((chunk + 1) / totalChunks) * 100);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      throw err;
    } finally {
      setIsUploading(false);
    }
  }, []);

  return { uploadFile, progress, isUploading, error };
};