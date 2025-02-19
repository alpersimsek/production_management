import React from 'react';
import { Trash2 } from 'lucide-react';
import { userService } from '../../services/api';
import type { User } from '../../types/api';

interface UserTableProps {
  users: User[];
  onUserDeleted: () => void;
}

const UserTable = ({ users, onUserDeleted }: UserTableProps) => {
  const [error, setError] = React.useState<string | null>(null);

  const handleDeleteUser = async (username: string) => {
    try {
      await userService.deleteUser(username);
      onUserDeleted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    }
  };

  const UserAvatar = ({ username }: { username: string }) => (
    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
      <span className="text-sm font-medium text-indigo-600">
        {username.charAt(0).toUpperCase()}
      </span>
    </div>
  );

  const RoleBadge = ({ role }: { role: string }) => (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        role === 'admin'
          ? 'bg-purple-100 text-purple-700'
          : 'bg-blue-100 text-blue-700'
      }`}
    >
      {role}
    </span>
  );

  const DeleteButton = ({ username }: { username: string }) => (
    <button
      onClick={() => handleDeleteUser(username)}
      className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
      title="Delete User"
    >
      <Trash2 className="h-4 w-4" />
    </button>
  );

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 text-red-700">
            <span className="font-medium">Error:</span>
            {error}
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">System Users</h2>
        </div>

        {users.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <p className="text-sm text-gray-500">No users found</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user) => (
                <tr 
                  key={user.username}
                  className="hover:bg-gray-50/50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <UserAvatar username={user.username} />
                      <span className="font-medium text-gray-900">
                        {user.username}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <RoleBadge role={user.role} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <DeleteButton username={user.username} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default UserTable;