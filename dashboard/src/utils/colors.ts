import { DisorderKey } from '../types';

export const DISORDER_COLORS: Record<DisorderKey, string> = {
  adhd: '#FF6B6B',
  anxiety: '#FFE66D',
  autism: '#4ECDC4',
  bipolar: '#A78BFA',
  cross: '#6B7280',
  eating: '#F472B6',
  mdd: '#3B82F6',
  ocd: '#F97316',
  other: '#9CA3AF',
  ptsd: '#EF4444',
  scz: '#10B981',
  substance: '#8B5CF6',
};

export const DISORDER_COLORS_DIM: Record<DisorderKey, string> = {
  adhd: 'rgba(255,107,107,0.15)',
  anxiety: 'rgba(255,230,109,0.15)',
  autism: 'rgba(78,205,196,0.15)',
  bipolar: 'rgba(167,139,250,0.15)',
  cross: 'rgba(107,114,128,0.15)',
  eating: 'rgba(244,114,182,0.15)',
  mdd: 'rgba(59,130,246,0.15)',
  ocd: 'rgba(249,115,22,0.15)',
  other: 'rgba(156,163,175,0.15)',
  ptsd: 'rgba(239,68,68,0.15)',
  scz: 'rgba(16,185,129,0.15)',
  substance: 'rgba(139,92,246,0.15)',
};

export const CHROMOSOME_COLORS = ['#3B82F6', '#64748B'];

export const PLOT_BG = 'rgba(0,0,0,0)';
export const PLOT_GRID = 'rgba(71,85,105,0.3)';
export const PLOT_TEXT = '#94a3b8';
export const PLOT_PAPER_BG = 'rgba(0,0,0,0)';

export const SIGNIFICANCE_LINE_COLOR = '#EF4444';
export const SUGGESTIVE_LINE_COLOR = '#F59E0B';
