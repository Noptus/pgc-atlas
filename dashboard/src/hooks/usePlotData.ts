import { useQuery } from '@tanstack/react-query';
import { fetchManhattan, fetchQQ, fetchHeatmap } from '../api/client';
import { DisorderKey } from '../types';

export function useManhattan(disorder: DisorderKey) {
  return useQuery({
    queryKey: ['manhattan', disorder],
    queryFn: () => fetchManhattan(disorder),
    staleTime: 120_000,
  });
}

export function useQQ(disorder: DisorderKey) {
  return useQuery({
    queryKey: ['qq', disorder],
    queryFn: () => fetchQQ(disorder),
    staleTime: 120_000,
  });
}

export function useHeatmap() {
  return useQuery({
    queryKey: ['heatmap'],
    queryFn: fetchHeatmap,
    staleTime: 300_000,
  });
}
