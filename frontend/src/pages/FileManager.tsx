import React, { useState } from 'react';
import {
  DocumentArrowUpIcon,
  DocumentCheckIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';
import { FileUpload } from '../components/file/FileUpload';
import { FileList } from '../components/file/FileList';
import { ProcessFileActions, ArchiveFileActions } from '../components/file/FileActions';
import { Modal } from '../components/shared/Modal';
import { Alert } from '../components/shared/Alert';
import { FOLDER_TYPES } from '../utils/constants';
import type { FolderType } from '../types/api';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

type Section = {
  name: string;
  icon: React.ElementType;
  folder: FolderType;
  action?: typeof ProcessFileActions | typeof ArchiveFileActions;
};

const FileManager: React.FC = () => {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<FolderType | null>(null);
  const [showProcessingModal, setShowProcessingModal] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleFileSelect = (filename: string, folder: FolderType) => {
    setSelectedFile(filename);
    setSelectedFolder(folder);
    setShowProcessingModal(true);
  };

  const handleProcessingComplete = () => {
    setShowProcessingModal(false);
    setSelectedFile(null);
    setSelectedFolder(null);
    setTimeout(() => setRefreshTrigger(prev => prev + 1), 500);
  };

  const sections: Section[] = [
    {
      name: 'Uploads',
      icon: DocumentArrowUpIcon,
      folder: FOLDER_TYPES.UPLOADS,
      action: ProcessFileActions,
    },
    {
      name: 'Processed',
      icon: DocumentCheckIcon,
      folder: FOLDER_TYPES.PROCESSED,
      action: ArchiveFileActions,
    },
    {
      name: 'Archives',
      icon: ArchiveBoxIcon,
      folder: FOLDER_TYPES.PROCESSED_ZIP,
    },
  ];

  if (!user) {
    return (
      <Alert type="error" title="Authentication Error">
        Please log in to access file management.
      </Alert>
    );
  }

  const getActionComponent = (folder: FolderType) => {
    const section = sections.find(s => s.folder === folder);
    return section?.action;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-8">
        {/* Header with Navigation */}
        <div className="flex items-center space-x-4 text-gray-500 hover:text-gray-700 transition-colors">
          <Link to="/dashboard" className="flex items-center space-x-2 text-sm">
            <ArrowLeft size={16} />
            <span>Back to Dashboard</span>
          </Link>
        </div>

        {/* Header & Upload Section */}
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-semibold text-gray-800">File Manager</h2>
          <FileUpload onUploadComplete={() => setRefreshTrigger(prev => prev + 1)} />
        </div>

        {/* File Sections */}
        <div className="grid gap-6">
          {sections.map((section) => (
            <div
              key={section.folder}
              className="bg-white shadow rounded-lg overflow-hidden transition-all hover:shadow-md"
            >
              <div className="flex items-center gap-3 p-4 border-b border-gray-100">
                <section.icon className="h-6 w-6 text-gray-500" />
                <h3 className="text-lg font-medium text-gray-800">{section.name}</h3>
              </div>
              
              <div className="p-4">
                <FileList 
                  folder={section.folder} 
                  onRefresh={() => setRefreshTrigger(prev => prev + 1)}
                  onFileSelect={(filename) => handleFileSelect(filename, section.folder)}
                  key={`${section.folder}-${refreshTrigger}`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Processing Modal */}
      {showProcessingModal && selectedFile && selectedFolder && (
        <Modal 
          isOpen={showProcessingModal} 
          onClose={() => setShowProcessingModal(false)} 
          title={selectedFolder === FOLDER_TYPES.UPLOADS ? "Process File" : "Create Archive"}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <DocumentCheckIcon className="h-6 w-6 text-gray-500" />
              <span className="text-sm text-gray-800">{selectedFile}</span>
            </div>
            {(() => {
              const ActionComponent = getActionComponent(selectedFolder);
              return ActionComponent ? (
                <ActionComponent 
                  filename={selectedFile} 
                  onComplete={handleProcessingComplete}
                />
              ) : null;
            })()}
          </div>
        </Modal>
      )}
    </div>
  );
};

export default FileManager;
