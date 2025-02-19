import { useState, useEffect } from 'react';
import { fileService } from '../services/api';
import type { GdprMapping } from '../types/api';

interface UseGdprSearchReturn {
  mappings: GdprMapping[] | null;
  isLoading: boolean;
  error: string | null;
  searchMappings: (term: string, type: 'all' | 'original' | 'masked') => Promise<void>;
  allMappings: GdprMapping[] | null;
}

const useGdprSearch = (): UseGdprSearchReturn => {
  const [mappings, setMappings] = useState<GdprMapping[] | null>(null);
  const [allMappings, setAllMappings] = useState<GdprMapping[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load all mappings on component mount
  useEffect(() => {
    loadAllMappings();
  }, []);

  const parseCsvToMappings = (text: string): GdprMapping[] => {
    return text
      .split('\n')
      .slice(1) // Skip header row
      .filter(row => row.trim()) // Remove empty rows
      .map(row => {
        const [type, original, masked] = row.split(',').map(val => val.trim());
        return { type, original, masked };
      });
  };

  const loadAllMappings = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const blob = await fileService.getGdprMap();
      const text = await blob.text();
      const parsedMappings = parseCsvToMappings(text);
      
      setAllMappings(parsedMappings);
      setMappings(parsedMappings); // Initially show all mappings
    } catch (error) {
      setError('Failed to load GDPR mappings. Please try again.');
      console.error('GDPR load error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchMappings = async (term: string, type: 'all' | 'original' | 'masked') => {
    if (!allMappings) return;

    try {
      setIsLoading(true);
      setError(null);

      if (!term.trim()) {
        setMappings(allMappings);
        return;
      }

      const filteredMappings = allMappings.filter(mapping => {
        const searchLower = term.toLowerCase();
        switch (type) {
          case 'original':
            return mapping.original.toLowerCase().includes(searchLower);
          case 'masked':
            return mapping.masked.toLowerCase().includes(searchLower);
          default:
            return (
              mapping.original.toLowerCase().includes(searchLower) ||
              mapping.masked.toLowerCase().includes(searchLower) ||
              mapping.type.toLowerCase().includes(searchLower)
            );
        }
      });

      setMappings(filteredMappings);
    } catch (error) {
      setError('Failed to search GDPR mappings. Please try again.');
      console.error('GDPR search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return { mappings, isLoading, error, searchMappings, allMappings };
};

export default useGdprSearch;