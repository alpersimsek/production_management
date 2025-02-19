import React, { useState, useMemo } from 'react';
import { Search, X, Filter, Download } from 'lucide-react';
import { FixedSizeList as List } from 'react-window';
import useGdprSearch from '../../hooks/useGdprSearch';
import type { GdprMapping } from '../../types/api';

type SearchField = 'all' | 'type' | 'original' | 'masked';

const GdprSearchForm: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchField, setSearchField] = useState<SearchField>('all');
  const [showFilters, setShowFilters] = useState(false);
  const { mappings, isLoading } = useGdprSearch();

  const filteredMappings = useMemo(() => {
    if (!mappings || !searchTerm.trim()) return mappings || [];

    const term = searchTerm.toLowerCase();
    return mappings.filter(mapping => {
      switch (searchField) {
        case 'type':
          return mapping.type.toLowerCase().includes(term);
        case 'original':
          return mapping.original.toLowerCase().includes(term);
        case 'masked':
          return mapping.masked.toLowerCase().includes(term);
        default:
          return (
            mapping.type.toLowerCase().includes(term) ||
            mapping.original.toLowerCase().includes(term) ||
            mapping.masked.toLowerCase().includes(term)
          );
      }
    });
  }, [mappings, searchTerm, searchField]);

  const uniqueTypes = useMemo(() => {
    if (!mappings) return [];
    return Array.from(new Set(mappings.map(m => m.type)));
  }, [mappings]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    if (!filteredMappings) return null;
    const item = filteredMappings[index];
    const isHighlighted = searchTerm && (
      (searchField === 'all' && (
        item.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.original.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.masked.toLowerCase().includes(searchTerm.toLowerCase())
      )) ||
      (searchField === 'type' && item.type.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (searchField === 'original' && item.original.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (searchField === 'masked' && item.masked.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
      <div 
        style={style} 
        className={`grid grid-cols-12 border-b border-gray-100 transition-colors ${
          isHighlighted ? 'bg-blue-50' : 'hover:bg-gray-50'
        }`}
      >
        <div className="col-span-2 p-3 truncate font-medium text-gray-600">{item.type}</div>
        <div className="col-span-5 p-3 truncate font-mono text-sm">{item.original}</div>
        <div className="col-span-5 p-3 truncate font-mono text-sm">{item.masked}</div>
      </div>
    );
  };

  const handleExport = () => {
    const csv = [
      ['Type', 'Original Value', 'Masked Value'],
      ...filteredMappings.map(m => [m.type, m.original, m.masked])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'gdpr-mappings.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4 bg-white rounded-xl shadow-lg border border-gray-200">
      {/* Header and Search Section */}
      <div className="p-4 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">GDPR Mappings</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Filter size={20} />
            </button>
            <button
              onClick={handleExport}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Download size={20} />
            </button>
          </div>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search mappings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-10 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
          )}
        </div>

        {showFilters && (
          <div className="flex gap-2 pt-2">
            <button
              onClick={() => setSearchField('all')}
              className={`px-3 py-1 rounded-full text-sm ${
                searchField === 'all' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All Fields
            </button>
            {['type', 'original', 'masked'].map((field) => (
              <button
                key={field}
                onClick={() => setSearchField(field as SearchField)}
                className={`px-3 py-1 rounded-full text-sm ${
                  searchField === field 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {field.charAt(0).toUpperCase() + field.slice(1)}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Stats Bar */}
      <div className="px-4 py-2 bg-gray-50 border-y border-gray-200 flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {isLoading ? (
            'Loading mappings...'
          ) : (
            <>
              Showing <span className="font-medium">{filteredMappings.length}</span> mapping
              {filteredMappings.length !== 1 ? 's' : ''}
              {searchTerm && ` for "${searchTerm}"`}
            </>
          )}
        </div>
        <div className="text-sm text-gray-500">
          {uniqueTypes.length} unique types
        </div>
      </div>

      {/* Header */}
      <div className="grid grid-cols-12 bg-gray-50 text-xs font-medium text-gray-500 uppercase sticky top-0">
        <div className="col-span-2 p-3">Type</div>
        <div className="col-span-5 p-3">Original Value</div>
        <div className="col-span-5 p-3">Masked Value</div>
      </div>

      {/* Virtualized List */}
      {isLoading ? (
        <div className="flex justify-center items-center h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      ) : (
        <List
          height={600}
          itemCount={filteredMappings.length}
          itemSize={44}
          width="100%"
          className="scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent hover:scrollbar-thumb-gray-300"
        >
          {Row}
        </List>
      )}
    </div>
  );
};

export default GdprSearchForm;