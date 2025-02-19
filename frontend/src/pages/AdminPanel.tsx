import React, { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { UserGroupIcon, PlusIcon } from '@heroicons/react/24/outline';
import { Menu, Transition } from '@headlessui/react';
import { useAuth } from '../context/AuthContext';
import UserTable from '../components/admin/UserTable';
import { CreateUserForm } from '../components/admin/CreateUserForm';
import { Alert } from '../components/shared/Alert';
import { userService } from '../services/api';
import { ArrowLeft } from 'lucide-react';

interface User {
  username: string;
  role: 'admin' | 'user';
}

const USERS_PER_PAGE = 10;

const AdminPanel: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [displayedUsers, setDisplayedUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const loadUsers = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await userService.listUsers();
      
      if (Array.isArray(response)) {
        setUsers(response);
        // Initialize displayed users with first page
        setDisplayedUsers(response.slice(0, USERS_PER_PAGE));
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = () => {
    const nextPage = page + 1;
    const start = page * USERS_PER_PAGE;
    const end = start + USERS_PER_PAGE;
    const newUsers = users.slice(start, end);
    
    if (newUsers.length > 0) {
      setDisplayedUsers(prev => [...prev, ...newUsers]);
      setPage(nextPage);
    }
  };

  const hasMore = users.length > displayedUsers.length;

  const handleUserCreated = async () => {
    setIsMenuOpen(false);
    setPage(1);
    await loadUsers();
  };

  const handleUserDeleted = async () => {
    setPage(1);
    await loadUsers();
  };

  useEffect(() => {
    loadUsers();
  }, []);

  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-4">

        {/* Header with Navigation */}
        <div className="flex items-center space-x-4 text-gray-500 hover:text-gray-700 transition-colors mb-5">
          <Link to="/dashboard" className="flex items-center space-x-2 text-sm">
            <ArrowLeft size={16} />
            <span>Back to Dashboard</span>
          </Link>
        </div>

        {/* Header with Add User Menu */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserGroupIcon className="h-5 w-5 text-gray-400" />
            <h1 className="text-lg font-medium text-gray-900">Users</h1>
            {users.length > 0 && (
              <span className="text-sm text-gray-500 ml-2">
                ({displayedUsers.length} of {users.length})
              </span>
            )}
          </div>

          <Menu as="div" className="relative">
            {({ open }) => (
              <>
                <Menu.Button 
                  className={`
                    inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 
                    text-sm font-medium transition-colors
                    ${open 
                      ? 'bg-gray-100 text-gray-900' 
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                  onClick={() => setIsMenuOpen(true)}
                >
                  <PlusIcon className="h-4 w-4" />
                  Add User
                </Menu.Button>
                
                <Transition
                  show={open && isMenuOpen}
                  as={React.Fragment}
                  enter="transition ease-out duration-200"
                  enterFrom="opacity-0 scale-95"
                  enterTo="opacity-100 scale-100"
                  leave="transition ease-in duration-150"
                  leaveFrom="opacity-100 scale-100"
                  leaveTo="opacity-0 scale-95"
                >
                  <Menu.Items
                    static
                    className="absolute right-0 mt-2 w-80 origin-top-right rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <div className="p-4">
                      <CreateUserForm 
                        onUserCreated={handleUserCreated}
                        onCancel={() => setIsMenuOpen(false)}
                      />
                    </div>
                  </Menu.Items>
                </Transition>
              </>
            )}
          </Menu>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert 
            type="error" 
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* User Table Section */}
        <div className="bg-white border border-gray-100 rounded-lg overflow-hidden">
          {users.length === 0 && !isLoading ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              No users found. Add your first user to get started.
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <UserTable 
                  users={displayedUsers}
                  onUserDeleted={handleUserDeleted}
                />
              </div>
              
              {hasMore && (
                <div className="px-4 py-3 border-t border-gray-100">
                  <button
                    onClick={loadMore}
                    disabled={isLoading}
                    className="w-full text-sm text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50"
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                        Loading more users...
                      </div>
                    ) : (
                      `Show More (${users.length - displayedUsers.length} remaining)`
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;