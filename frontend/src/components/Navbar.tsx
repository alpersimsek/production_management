import React, { Fragment } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Transition } from '@headlessui/react';
import { UserIcon, Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';

interface NavigationItem {
  name: string;
  href: string;
  requiresAdmin?: boolean;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Files', href: '/files' },
  { name: 'Users', href: '/admin', requiresAdmin: true },
  { name: 'GDPR Search', href: '/gdpr-search' }
];

export const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  
  const isCurrentPage = (href: string): boolean => location.pathname === href;
  
  const filteredNavigation = navigation.filter(
    item => !item.requiresAdmin || user?.role === 'admin'
  );

  return (
    <nav className="bg-white border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link 
            to="/" 
            className="text-xl font-medium text-gray-900 hover:text-gray-700 transition"
          >
            GDPR
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-x-8">
            {filteredNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`text-sm transition-colors ${
                  isCurrentPage(item.href)
                    ? 'text-blue-600 font-medium'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.name}
              </Link>
            ))}

            {/* Profile Menu */}
            <Menu as="div" className="relative">
              <Menu.Button className="flex items-center">
                <UserIcon className="h-8 w-8 text-gray-600 hover:text-gray-900 transition p-1.5" />
              </Menu.Button>
              <Transition
                as={Fragment}
                enter="transition ease-out duration-100"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
              >
                <Menu.Items className="absolute right-0 mt-2 w-48 rounded-lg bg-white py-2 shadow-lg ring-1 ring-gray-100">
                  <div className="px-4 py-2">
                    <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                    <p className="text-xs text-gray-500">{user?.role}</p>
                  </div>
                  <div className="border-t border-gray-100 mt-2">
                    <Menu.Item>
                      {({ active }) => (
                        <button
                          onClick={logout}
                          className={`w-full text-left px-4 py-2 text-sm ${
                            active ? 'bg-gray-50 text-gray-900' : 'text-gray-600'
                          }`}
                        >
                          Sign out
                        </button>
                      )}
                    </Menu.Item>
                  </div>
                </Menu.Items>
              </Transition>
            </Menu>
          </div>

          {/* Mobile Menu Button */}
          <button className="md:hidden p-2 text-gray-600 hover:text-gray-900 transition">
            <Bars3Icon className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Mobile Menu (hidden by default) */}
      <div className="hidden md:hidden border-t border-gray-100">
        <div className="px-4 py-3 space-y-3">
          {filteredNavigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`block text-sm ${
                isCurrentPage(item.href)
                  ? 'text-blue-600 font-medium'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {item.name}
            </Link>
          ))}
          <button
            onClick={logout}
            className="block w-full text-left text-sm text-gray-600 hover:text-gray-900 pt-3 border-t border-gray-100"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;