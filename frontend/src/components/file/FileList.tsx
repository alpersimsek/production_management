import React, { useState, useEffect } from 'react';
import { 
  DocumentIcon, 
  ArrowDownTrayIcon,
  TrashIcon,
  PlayIcon,
  ArchiveBoxIcon,
  FolderIcon 
} from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';
import { fileService } from '../../services/api';
import type { FolderType } from '../../types/api';
import { FOLDER_TYPES } from '../../utils/constants';

interface FileData {
  filename: string;
}

interface FileListProps {
  folder: FolderType;
  onRefresh?: () => void;
  onFileSelect?: (filename: string) => void;
}

export const FileList: React.FC<FileListProps> = ({
  folder,
  onRefresh,
  onFileSelect
}) => {
  const { user } = useAuth();
  const [files, setFiles] = useState<FileData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFiles = async () => {
    if (!user) return;
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fileService.listFiles(user.username, folder);
      setFiles(response.files.map(filename => ({ filename })));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [folder, user]);

  const handleDownload = async (filename: string) => {
    if (!user) return;
    try {
      const blob = await fileService.downloadFile(user.username, filename);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download file');
    }
  };

  const handleDelete = async (filename: string) => {
    if (!user) return;
    try {
      await fileService.deleteFile(user.username, folder, filename);
      await loadFiles();
      if (onRefresh) onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-800"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-100 rounded-lg p-4 text-sm text-red-600 flex items-center justify-between">
          {error}
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
            X
          </button>
        </div>
      )}

      <div className="space-y-2">
        {files.length === 0 ? (
          <div className="text-center py-12">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-300" />
            <p className="mt-2 text-sm text-gray-500">No files in {folder} folder</p>
          </div>
        ) : (
          files.map((file) => (
            <div 
              key={file.filename}
              className="group flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-50 rounded-lg group-hover:bg-gray-100 transition-colors">
                  <DocumentIcon className="h-5 w-5 text-gray-400" />
                </div>
                <span className="text-sm text-gray-900">{file.filename}</span>
              </div>

              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {folder === FOLDER_TYPES.UPLOADS && (
                  <button
                    onClick={() => onFileSelect?.(file.filename)}
                    className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-md transition-colors"
                    title="Process File"
                  >
                    <PlayIcon className="h-4 w-4" />
                  </button>
                )}
                {folder === FOLDER_TYPES.PROCESSED && (
                  <button
                    onClick={() => onFileSelect?.(file.filename)}
                    className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-md transition-colors"
                    title="Archive File"
                  >
                    <ArchiveBoxIcon className="h-4 w-4" />
                  </button>
                )}
                {folder === FOLDER_TYPES.PROCESSED_ZIP && (
                  <button
                  onClick={() => handleDownload(file.filename)}
                  className="p-1.5 text-gray-500 hover:bg-gray-50 rounded-md transition-colors"
                  title="Download"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                </button>
                )}
                {/* <button
                  onClick={() => handleDownload(file.filename)}
                  className="p-1.5 text-gray-500 hover:bg-gray-50 rounded-md transition-colors"
                  title="Download"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                </button> */}
                <button
                  onClick={() => handleDelete(file.filename)}
                  className="p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors"
                  title="Delete"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FileList;