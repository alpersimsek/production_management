import { useState, useEffect, useCallback } from 'react';
import { fileService } from '../services/api';
import type { ProcessingProgress } from '../types/api';

interface UseProcessingStatusProps {
  taskId: string;
  type: 'process' | 'mask' | 'archive';
  onComplete?: () => void;
  pollingInterval?: number;
}

interface UseProcessingStatusResult {
  progress: number;
  error: string | null;
  isCompleted: boolean;
  startPolling: () => void;
  stopPolling: () => void;
}

export const useProcessingStatus = ({
  taskId,
  type,
  onComplete,
  pollingInterval = 1000
}: UseProcessingStatusProps): UseProcessingStatusResult => {
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isPolling, setIsPolling] = useState(true);

  const checkProgress = useCallback(async () => {
    try {
      let response: ProcessingProgress;
      
      switch (type) {
        case 'process':
          response = await fileService.checkProcessingProgress(taskId);
          break;
        case 'mask':
          response = await fileService.checkMaskingProgress(taskId);
          break;
        case 'archive':
          response = await fileService.checkArchiveProgress(taskId);
          break;
        default:
          throw new Error('Invalid processing type');
      }

      setProgress(response.progress);

      if (response.progress >= 100) {
        setIsCompleted(true);
        setIsPolling(false);
        if (onComplete) {
          onComplete();
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check progress');
      setIsPolling(false);
    }
  }, [taskId, type, onComplete]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isPolling && !isCompleted && !error) {
      checkProgress();
      intervalId = setInterval(checkProgress, pollingInterval);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [checkProgress, isPolling, isCompleted, error, pollingInterval]);

  const startPolling = useCallback(() => {
    setIsPolling(true);
  }, []);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  return {
    progress,
    error,
    isCompleted,
    startPolling,
    stopPolling
  };
};