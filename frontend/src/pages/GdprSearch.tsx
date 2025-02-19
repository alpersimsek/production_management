import React from 'react';
import { FileSearch, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import GdprSearchForm from '../components/gdpr/GdprSearchForm';

const GdprSearch: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
      {/* Header with Navigation */}
      <div className="flex items-center space-x-4 text-gray-500 hover:text-gray-700 transition-colors">
        <Link to="/dashboard" className="flex items-center space-x-2 text-sm">
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>
      </div>

      {/* Page Title */}
      <div className="space-y-1">
        <div className="flex items-center space-x-3">
          <FileSearch className="h-6 w-6 text-indigo-500" />
          <h1 className="text-2xl font-semibold text-gray-900">GDPR Mapping Search</h1>
        </div>
        <p className="text-base text-gray-600 max-w-2xl">
          Search through your GDPR mappings to find corresponding masked and original values. 
          Use filters to narrow down specific types of data.
        </p>
      </div>

      {/* Main Content */}
      <div className="pt-4">
        <GdprSearchForm />
      </div>

      {/* Optional Help Text */}
      <div className="mt-6 text-sm text-gray-500 max-w-2xl">
        <p>
          Tip: Use the search filters above to quickly find specific types of masked data. 
          You can export your search results using the download button.
        </p>
      </div>
    </div>
  );
};

export default GdprSearch;