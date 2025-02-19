import React, { useEffect, useCallback, useState } from 'react';
import { fileService } from '../../services/api';
import { Alert } from '../shared/Alert';

interface ProcessingStatusProps {
  taskId: string;
  onComplete: () => void;
  type: 'process' | 'mask' | 'archive';
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  taskId,
  onComplete,
  type
}) => {
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const checkProgress = useCallback(async () => {
    try {
      let response;
      console.log(`Checking progress for ${type} with taskId:`, taskId);
      
      switch (type) {
        case 'process':
          response = await fileService.checkProcessingProgress(taskId);
          break;
        case 'mask':
          // No need to replace, the API gives us maskTask_id directly
          response = await fileService.checkMaskingProgress(taskId);
          break;
        case 'archive':
          // No need to replace, the API gives us zipMaskTask_id directly
          response = await fileService.checkArchiveProgress(taskId);
          break;
      }

      console.log(`Progress response for ${type}:`, response);

      if (response && typeof response.progress === 'number') {
        setProgress(response.progress);

        if (response.progress >= 100) {
          console.log(`${type} completed`);
          setIsCompleted(true);
          onComplete();
        }
      }
    } catch (err) {
      console.error('Progress check error:', err, 'for type:', type, 'taskId:', taskId);
      setError(err instanceof Error ? err.message : 'Failed to check progress');
    }
  }, [taskId, type, onComplete]);

  useEffect(() => {
    if (isCompleted || error) return;

    // Initial check
    checkProgress();

    const interval = setInterval(checkProgress, 1000);
    return () => clearInterval(interval);
  }, [checkProgress, isCompleted, error]);

  if (error) {
    return (
      <Alert type="error" onClose={() => setError(null)}>
        {error}
      </Alert>
    );
  }

  const getStatusMessage = () => {
    switch (type) {
      case 'process':
        return 'Processing file...';
      case 'mask':
        return 'Masking PII data...';
      case 'archive':
        return 'Creating archive...';
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm text-gray-600">
        <span>{getStatusMessage()}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="relative pt-1">
        <div className="overflow-hidden h-2 text-xs flex rounded bg-blue-100">
          <div
            style={{ width: `${progress}%` }}
            className={`
              shadow-none flex flex-col text-center whitespace-nowrap text-white 
              justify-center
              ${isCompleted ? 'bg-green-500' : 'bg-blue-500'}
              transition-all duration-300 ease-in-out
            `}
          />
        </div>
      </div>
    </div>
  );
};