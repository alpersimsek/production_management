import React, { useState } from 'react';
import { UserPlusIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Input } from '../shared/Input';
import { Button } from '../shared/Button';
import { Alert } from '../shared/Alert';
import { userService } from '../../services/api';
import { validatePassword } from '../../utils/constants';

interface CreateUserFormProps {
  onUserCreated: () => void;
  onCancel: () => void;
}

interface FormData {
  username: string;
  password: string;
}

interface FormError {
  message: string;
  field?: keyof FormData;
}

export const CreateUserForm: React.FC<CreateUserFormProps> = ({ 
  onUserCreated,
  onCancel 
}) => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    password: ''
  });
  const [error, setError] = useState<FormError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate password
    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      setError({ message: passwordError, field: 'password' });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await userService.createUser({
        ...formData,
        role: 'user'
      });
      
      onUserCreated();
    } catch (err) {
      setError({ 
        message: err instanceof Error ? err.message : 'Failed to create user'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error?.field === name) {
      setError(null);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-gray-900">Add New User</h2>
        <button
          type="button"
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-500 transition-colors"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="text-sm text-red-600">
          {error.message}
        </div>
      )}

      {/* Form Fields */}
      <div className="space-y-3">
        <Input
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
          placeholder="Username"
          className="text-sm"
        />

        <Input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          placeholder="Password"
          className="text-sm"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-2 pt-2">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          size="sm"
          className="text-sm"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          isLoading={isLoading}
          disabled={!formData.username || !formData.password}
          size="sm"
          className="text-sm"
        >
          {isLoading ? 'Creating...' : 'Create User'}
        </Button>
      </div>
    </form>
  );
};

export default CreateUserForm;