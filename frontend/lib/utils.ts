import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;

  return date.toLocaleDateString();
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

export function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

import type { AgentType } from '@/types';

export function getAgentColor(agentType: AgentType): string {
  const colors: Record<AgentType, string> = {
    requirements: '#00E5FF',
    cad: '#9D4EDD',
    validation: '#00FF88',
    export: '#FFB020',
    user: '#FFFFFF',
    system: '#64748B',
  };
  return colors[agentType] || '#64748B';
}

export function getAgentName(agentType: AgentType): string {
  const names: Record<AgentType, string> = {
    requirements: 'Requirements Agent',
    cad: 'CAD Agent',
    validation: 'Validation Agent',
    export: 'Export Agent',
    user: 'You',
    system: 'System',
  };
  return names[agentType] || 'Unknown';
}

export function getAgentIcon(agentType: AgentType): string {
  const icons: Record<AgentType, string> = {
    requirements: 'search',
    cad: 'box',
    validation: 'check-circle',
    export: 'download',
    user: 'user',
    system: 'info',
  };
  return icons[agentType] || 'info';
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    processing: '#00E5FF',
    generating: '#9D4EDD',
    validating: '#00FF88',
    exporting: '#FFB020',
    complete: '#00FF88',
    failed: '#FF4444',
    pending: '#64748B',
  };
  return colors[status] || '#64748B';
}

export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
