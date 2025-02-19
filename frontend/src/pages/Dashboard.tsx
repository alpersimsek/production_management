import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fileService, userService } from '../services/api';
import type { FileListResponse, User } from '../types/api';
import { 
  Files, 
  FileCheck, 
  Archive, 
  Users, 
  ChevronDown, 
  ChevronUp,
  Activity
} from 'lucide-react';

const FOLDERS = {
  UPLOADS: 'uploads',
  PROCESSED: 'processed',
  PROCESSED_ZIP: 'processed_zip'
} as const;

interface DashboardStats {
  uploads: string[];
  processed: string[];
  processed_zip: string[];
  users?: User[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    uploads: [],
    processed: [],
    processed_zip: []
  });
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!user?.username) return;
      try {
        setIsLoading(true);
        const [uploadsData, processedData, processedZipData] = await Promise.all([
          fileService.listFiles(user.username, FOLDERS.UPLOADS),
          fileService.listFiles(user.username, FOLDERS.PROCESSED),
          fileService.listFiles(user.username, FOLDERS.PROCESSED_ZIP)
        ]);

        let adminStats = {};
        if (user.role === 'admin') {
          const users = await userService.listUsers();
          adminStats = { users };
        }

        setStats({
          uploads: uploadsData.files,
          processed: processedData.files,
          processed_zip: processedZipData.files,
          ...adminStats
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [user]);

  const StatCard = ({ 
    id,
    icon: Icon, 
    label, 
    count, 
    items,
  }: { 
    id: string;
    icon: any;
    label: string;
    count: number;
    items: string[];
  }) => {
    const isExpanded = expandedCard === id;
    const hasRecentItems = items.length > 0;
    const recentItem = items[0];

    return (
      <div className="bg-white rounded-lg border border-gray-100">
        <button 
          onClick={() => setExpandedCard(isExpanded ? null : id)}
          className="w-full text-left p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 rounded-md bg-gray-50">
                <Icon className="h-5 w-5 text-gray-500" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-400">{label}</div>
                <div className="text-2xl font-semibold text-gray-900 mt-1">{count}</div>
                {hasRecentItems && !isExpanded && (
                  <div className="text-xs text-gray-500 mt-1 truncate max-w-[200px]">
                    Latest: {recentItem}
                  </div>
                )}
              </div>
            </div>
            {items.length > 0 && (
              <div className="text-gray-400">
                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </div>
            )}
          </div>
        </button>
        
        {isExpanded && items.length > 0 && (
          <div className="px-6 pb-6">
            <div className="h-px w-full bg-gray-50 mb-4" />
            <div className="space-y-2">
              {items.slice(0, 3).map(item => (
                <div key={item} className="text-sm text-gray-600">
                  {item}
                </div>
              ))}
              {items.length > 3 && (
                <button className="text-xs font-medium text-gray-400 hover:text-gray-600 mt-2">
                  +{items.length - 3} more
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const UsersPreview = ({ users }: { users: User[] }) => {
    const isExpanded = expandedCard === 'users';
    const displayCount = 5;

    return (
      <div className="bg-white rounded-lg border border-gray-100">
        <button 
          onClick={() => setExpandedCard(isExpanded ? null : 'users')}
          className="w-full text-left p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 rounded-md bg-gray-50">
                <Users className="h-5 w-5 text-gray-500" />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-400">System Users</div>
                <div className="text-2xl font-semibold text-gray-900 mt-1">{users.length}</div>
                {!isExpanded && (
                  <div className="flex -space-x-2 mt-3">
                    {users.slice(0, 3).map((user) => (
                      <div
                        key={user.username}
                        className="w-6 h-6 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center"
                      >
                        <span className="text-xs font-medium text-gray-600">
                          {user.username[0].toUpperCase()}
                        </span>
                      </div>
                    ))}
                    {users.length > 3 && (
                      <div className="w-6 h-6 rounded-full bg-gray-50 border-2 border-white flex items-center justify-center">
                        <span className="text-xs text-gray-500">+{users.length - 3}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="text-gray-400">
              {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>
          </div>
        </button>

        {isExpanded && (
          <div className="px-6 pb-6">
            <div className="h-px w-full bg-gray-50 mb-4" />
            <div className="space-y-2">
              {users.slice(0, displayCount).map((user) => (
                <div key={user.username} className="flex items-center space-x-3">
                  <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-600">
                      {user.username[0].toUpperCase()}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">{user.username}</span>
                </div>
              ))}
              {users.length > displayCount && (
                <button className="text-xs font-medium text-gray-400 hover:text-gray-600 mt-2">
                  +{users.length - displayCount} more
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Activity className="h-8 w-8 text-gray-400 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8 space-y-1">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Welcome back, {user?.username}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          id="uploads"
          icon={Files} 
          label="Uploads" 
          count={stats.uploads.length}
          items={stats.uploads}
        />
        <StatCard 
          id="processed"
          icon={FileCheck} 
          label="Processed Files" 
          count={stats.processed.length}
          items={stats.processed}
        />
        <StatCard 
          id="archives"
          icon={Archive} 
          label="Processed Archives" 
          count={stats.processed_zip.length}
          items={stats.processed_zip}
        />
        {user?.role === 'admin' && stats.users && (
          <UsersPreview users={stats.users} />
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <Link 
          to="/files" 
          className="group p-4 bg-white rounded-lg border border-gray-100 hover:border-gray-200 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-md bg-gray-50 group-hover:bg-gray-100 transition-colors">
              <Files className="h-5 w-5 text-gray-500" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">File Management</h3>
              <p className="text-sm text-gray-500">Upload and process files</p>
            </div>
          </div>
        </Link>

        {user?.role === 'admin' && (
          <Link 
            to="/admin" 
            className="group p-4 bg-white rounded-lg border border-gray-100 hover:border-gray-200 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-md bg-gray-50 group-hover:bg-gray-100 transition-colors">
                <Users className="h-5 w-5 text-gray-500" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-900">User Management</h3>
                <p className="text-sm text-gray-500">Manage system users</p>
              </div>
            </div>
          </Link>
        )}
      </div>
    </div>
  );
};

export default Dashboard;