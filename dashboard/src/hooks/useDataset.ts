import { useQuery } from '@tanstack/react-query';
import { fetchDatasets, fetchVariants, searchVariant, DISORDERS } from '../api/client';
import { DisorderKey } from '../types';

export function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: fetchDatasets,
    staleTime: Infinity,
  });
}

export function useDisorder(id: DisorderKey) {
  return DISORDERS[id];
}

export function useVariants(disorder: DisorderKey, n = 50) {
  return useQuery({
    queryKey: ['variants', disorder, n],
    queryFn: () => fetchVariants(disorder, n),
    staleTime: 60_000,
  });
}

export function useSearch(query: string) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => searchVariant(query),
    enabled: query.length > 2,
    staleTime: 30_000,
  });
}
