import React from 'react';
import { Button } from '@/components/ui/button';

interface DebugInfo {
  timestamp: string;
  level: 'info' | 'warn' | 'error';
  message: string;
  data?: any;
}

interface VoiceDebugLogProps {
  logs: DebugInfo[];
  onClear: () => void;
}

const getLogLevelColor = (level: DebugInfo['level']) => {
  if (level === 'error') return 'text-red-600';
  if (level === 'warn') return 'text-yellow-600';
  return 'text-foreground';
};

export const VoiceDebugLog: React.FC<VoiceDebugLogProps> = ({ logs, onClear }) => (
  <div className="mt-4 p-3 bg-muted rounded-lg max-h-64 overflow-y-auto">
    <div className="flex justify-between items-center mb-2">
      <h4 className="font-medium">Debug Logs</h4>
      <Button variant="ghost" size="sm" onClick={onClear}>Clear</Button>
    </div>
    <div className="space-y-1 font-mono text-xs">
      {logs.map((log, index) => (
        <div key={index} className={getLogLevelColor(log.level)}>
          <span className="text-muted-foreground">[{log.timestamp}]</span>{' '}
          <span className="font-semibold">{log.level.toUpperCase()}</span> {log.message}
          {log.data && (
            <details className="mt-1 ml-4">
              <summary className="cursor-pointer text-muted-foreground">Show data</summary>
              <pre className="mt-1 p-2 bg-background rounded overflow-x-auto">
                {JSON.stringify(log.data, null, 2)}
              </pre>
            </details>
          )}
        </div>
      ))}
    </div>
  </div>
);