import React, { useState } from 'react';
import { EyeIcon, SlashIcon, MinusIcon, ArrowUpCircle } from 'lucide-react';
import { FOLDER_TYPES } from '../../utils/constants';
import { FileList } from './FileList';
import { FileUpload } from './FileUpload';
import type { FolderType } from '../../types/api';

type ColumnVisibility = {
  [K in FolderType]: boolean;
};

interface ColumnHeaderProps {
  folderType: FolderType;
  title: string;
  isMinimized: boolean;
  onToggleMinimize: () => void;
  onToggleVisibility: () => void;
}

const FileColumnsLayout: React.FC = () => {
  const [visibleColumns, setVisibleColumns] = useState<ColumnVisibility>({
    [FOLDER_TYPES.UPLOADS]: true,
    [FOLDER_TYPES.PROCESSED]: true,
    [FOLDER_TYPES.PROCESSED_ZIP]: true
  });

  const [minimizedColumns, setMinimizedColumns] = useState<ColumnVisibility>({
    [FOLDER_TYPES.UPLOADS]: false,
    [FOLDER_TYPES.PROCESSED]: false,
    [FOLDER_TYPES.PROCESSED_ZIP]: false
  });

  const toggleColumnVisibility = (folderType: FolderType): void => {
    setVisibleColumns(prev => ({
      ...prev,
      [folderType]: !prev[folderType]
    }));
  };

  const toggleColumnMinimize = (folderType: FolderType): void => {
    setMinimizedColumns(prev => ({
      ...prev,
      [folderType]: !prev[folderType]
    }));
  };

  const ColumnHeader: React.FC<ColumnHeaderProps> = ({
    folderType,
    title,
    isMinimized,
    onToggleMinimize,
    onToggleVisibility
  }) => (
    <div className="flex items-center justify-between bg-gray-100 p-3 rounded-t-lg">
      <div className="flex items-center gap-2">
        <h2 className="font-semibold text-gray-700">{title}</h2>
      </div>
      <div className="flex gap-2">
        <button
          onClick={onToggleMinimize}
          className="p-1 hover:bg-gray-200 rounded-md"
        >
          {isMinimized ? (
            <ArrowUpCircle className="w-5 h-5 text-gray-600" />
          ) : (
            <MinusIcon className="w-5 h-5 text-gray-600" />
          )}
        </button>
        <button
          onClick={onToggleVisibility}
          className="p-1 hover:bg-gray-200 rounded-md"
        >
          {visibleColumns[folderType] ? (
            <EyeIcon className="w-5 h-5 text-gray-600" />
          ) : (
            <SlashIcon className="w-5 h-5 text-gray-600" />
          )}
        </button>
      </div>
    </div>
  );

  return (
    <div className="p-4">
      <div className="mb-6">
        <FileUpload />
      </div>
      
      <div className="flex gap-4 min-h-0 overflow-hidden">
        {Object.entries(visibleColumns).map(([folderType, isVisible]) => (
          isVisible && (
            <div key={folderType} className="flex-1 flex flex-col min-w-[350px] bg-white rounded-lg shadow-md">
              <ColumnHeader
                folderType={folderType as FolderType}
                title={
                  folderType === FOLDER_TYPES.UPLOADS ? "Uploaded Files" :
                  folderType === FOLDER_TYPES.PROCESSED ? "Processed Files" :
                  "Archived Files"
                }
                isMinimized={minimizedColumns[folderType as FolderType]}
                onToggleMinimize={() => toggleColumnMinimize(folderType as FolderType)}
                onToggleVisibility={() => toggleColumnVisibility(folderType as FolderType)}
              />
              
              {!minimizedColumns[folderType as FolderType] && (
                <div className="flex-1 overflow-y-auto p-4">
                  <FileList
                    folder={folderType as FolderType}
                    onRefresh={() => {/* Will be implemented */}}
                  />
                </div>
              )}
            </div>
          )
        ))}
      </div>
      
      <div className="fixed bottom-4 right-4 flex gap-2">
        {Object.entries(visibleColumns).map(([folderType, isVisible]) => !isVisible && (
          <button
            key={folderType}
            onClick={() => toggleColumnVisibility(folderType as FolderType)}
            className="flex items-center space-x-2 bg-white px-4 py-2 rounded-md shadow-lg hover:bg-gray-50"
          >
            <EyeIcon className="w-5 h-5 text-gray-600" />
            <span className="ml-2">
              Show {
                folderType === FOLDER_TYPES.UPLOADS ? "Uploads" :
                folderType === FOLDER_TYPES.PROCESSED ? "Processed" :
                "Archives"
              }
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default FileColumnsLayout;