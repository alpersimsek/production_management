import React, { useCallback, useState } from 'react';
import { FileRejection, useDropzone } from 'react-dropzone';
import { FolderIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';
import { useFileUpload } from '../../hooks/useFileUpload';
import { Button } from '../shared/Button';
import { Alert } from '../shared/Alert';
import { ALLOWED_FILE_TYPES } from '../../utils/constants';
import { formatBytes } from '../../utils/constants';

interface FileUploadProps {
  onUploadComplete?: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const { user } = useAuth();
  const { uploadFile, progress, isUploading, error } = useFileUpload();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDropRejected = useCallback((rejectedFiles: FileRejection[]) => {
    rejectedFiles.forEach(({ file, errors }) => {
      if (file.type === '' || file.type === undefined) {
        console.log(`Mime type for ${file.name} is not detected. Assuming as a text file.`);
        const newFile = new File([file], file.name, {type:'text/plain'})
        onDrop([newFile])
      } else {
      console.warn('Rejected File:', file.name, 'Mime:', file.type);
      errors.forEach((error) => console.error(error.message));
      }
    });
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      console.log('Accepted File:', file.name, 'Mime:', file.type);
    });
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    maxFiles: 1,
    accept: ALLOWED_FILE_TYPES.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
  });

  const handleUpload = async () => {
    if (selectedFile && user) {
      try {
        await uploadFile(selectedFile, user.username);
        setSelectedFile(null);
        onUploadComplete?.(); // Call the callback after successful upload
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert type="error" title="Upload Error">
          {error}
        </Alert>
      )}

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
          ${selectedFile ? 'bg-gray-50' : 'hover:border-gray-400'}
          transition-colors duration-200 cursor-pointer
        `}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
          {selectedFile ? (
            <div className="mt-4 flex items-center justify-center space-x-2">
              <span className="text-sm text-gray-900">{selectedFile.name}</span>
              <span className="text-sm text-gray-500">
                ({formatBytes(selectedFile.size)})
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearSelection();
                }}
                className="text-gray-400 hover:text-gray-500"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                {isDragActive
                  ? 'Drop the file here'
                  : 'Drag and drop a file here, or click to select'}
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supported files: ZIP, TAR, GZ, TXT, CSV, PCAP
              </p>
              <p className="text-xs text-gray-500">
                Maximum file size: {formatBytes(2 * 1024 * 1024 * 1024)}
              </p>
            </div>
          )}
        </div>
      </div>

      {selectedFile && (
        <div className="flex justify-end">
          <Button
            onClick={handleUpload}
            isLoading={isUploading}
            disabled={!selectedFile || isUploading}
          >
            Upload File
          </Button>
        </div>
      )}

      {isUploading && (
        <div className="mt-4">
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <div>
                <span className="text-xs font-semibold inline-block text-blue-600">
                  Uploading...
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold inline-block text-blue-600">
                  {Math.round(progress)}%
                </span>
              </div>
            </div>
            <div className="overflow-hidden h-2 text-xs flex rounded bg-blue-100">
              <div
                style={{ width: `${progress}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-200"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};