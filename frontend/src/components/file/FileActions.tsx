import React, { useState } from 'react';
import { PlayIcon, CheckCircleIcon, FolderIcon, ShieldCheckIcon, ArchiveBoxIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';
import { fileService } from '../../services/api';
import { Button } from '../shared/Button';
import { Alert } from '../shared/Alert';
import { ProcessingStatus } from './ProcessingStatus';

interface BaseFileActionsProps {
  filename: string;
  onComplete?: () => void;
}

// Combined process and mask for uploads folder
export const ProcessFileActions: React.FC<BaseFileActionsProps> = ({
  filename,
  onComplete
}) => {
  const { user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<'idle' | 'processing' | 'masking' | 'completed'>('idle');
  const [taskId, setTaskId] = useState<string | null>(null);

  const startProcessing = async () => {
    if (!user) return;
    setError(null);
    setCurrentStage('processing');
    try {
      const response = await fileService.processFile(filename, user.username);
      setTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing');
      setCurrentStage('idle');
    }
  };

  const startMasking = async () => {
    if (!user) return;
    setError(null);
    setCurrentStage('masking');
    try {
      const response = await fileService.maskFile(filename, user.username);
      setTaskId(response.maskTask_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start masking');
      setCurrentStage('processing');
    }
  };

  const handleProcessingComplete = () => {
    setTaskId(null);
    if (currentStage === 'processing') {
      startMasking();
    } else if (currentStage === 'masking') {
      setCurrentStage('completed');
      if (onComplete) onComplete();
    }
  };

  const getCurrentStatus = () => {
    switch (currentStage) {
      case 'processing':
        return <ProcessingStatus
          taskId={taskId!}
          onComplete={handleProcessingComplete}
          type="process"
        />;
      case 'masking':
        return <ProcessingStatus
          taskId={taskId!}
          onComplete={handleProcessingComplete}
          type="mask"
        />;
      default:
        return null;
    }
  };

  const getStageIcon = () => {
    switch (currentStage) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'masking':
        return <ShieldCheckIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <FolderIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getStageText = () => {
    switch (currentStage) {
      case 'processing':
        return 'Processing...';
      case 'masking':
        return 'Masking PII Data...';
      case 'completed':
        return 'Processing Complete';
      default:
        return 'Extract and Process';
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getStageIcon()}
          <span>{getStageText()}</span>
        </div>
        {currentStage === 'idle' && (
          <Button onClick={startProcessing} size="sm">
            Start Processing
          </Button>
        )}
      </div>

      {taskId && getCurrentStatus()}

      {currentStage === 'completed' && (
        <Alert type="success">Processing and masking completed successfully</Alert>
      )}
    </div>
  );
};

// Archive action for processed files
export const ArchiveFileActions: React.FC<BaseFileActionsProps> = ({
  filename,
  onComplete
}) => {
  const { user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [archiveTaskId, setArchiveTaskId] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const createArchive = async () => {
    if (!user) return;
    setError(null);
    try {
      const response = await fileService.createFinalArchive(filename, user.username);
      setArchiveTaskId(response.zipMaskTask_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create archive');
    }
  };

  const handleArchiveComplete = () => {
    setIsCompleted(true);
    setArchiveTaskId(null);
    if (onComplete) onComplete();
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ArchiveBoxIcon className="h-5 w-5 text-purple-500" />
          <span>Create Archive</span>
        </div>
        {!isCompleted && !archiveTaskId && (
          <Button onClick={createArchive} size="sm">
            Create Archive
          </Button>
        )}
      </div>

      {archiveTaskId && (
        <ProcessingStatus
          taskId={archiveTaskId}
          onComplete={handleArchiveComplete}
          type="archive"
        />
      )}

      {isCompleted && (
        <Alert type="success">Archive created successfully</Alert>
      )}
    </div>
  );
};