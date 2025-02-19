import React from 'react';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/solid';

interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  onClose,
}) => {
  const styles = {
    success: {
      bg: 'bg-green-50',
      icon: <CheckCircleIcon className="h-5 w-5 text-green-400" />,
      border: 'border-green-400',
      text: 'text-green-800',
    },
    error: {
      bg: 'bg-red-50',
      icon: <XCircleIcon className="h-5 w-5 text-red-400" />,
      border: 'border-red-400',
      text: 'text-red-800',
    },
    warning: {
      bg: 'bg-yellow-50',
      icon: <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />,
      border: 'border-yellow-400',
      text: 'text-yellow-800',
    },
    info: {
      bg: 'bg-blue-50',
      icon: <InformationCircleIcon className="h-5 w-5 text-blue-400" />,
      border: 'border-blue-400',
      text: 'text-blue-800',
    },
  };

  return (
    <div className={`rounded-lg p-4 ${styles[type].bg} border ${styles[type].border}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          {styles[type].icon}
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${styles[type].text}`}>
              {title}
            </h3>
          )}
          <div className={`text-sm ${styles[type].text}`}>{children}</div>
        </div>
        {onClose && (
          <button
            type="button"
            className={`ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 focus:ring-2 focus:ring-offset-2 ${styles[type].text}`}
            onClick={onClose}
          >
            <span className="sr-only">Dismiss</span>
            <XCircleIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};