import React from 'react';
import { Badge } from '@/components/ui/badge';

interface VoiceStatusIndicatorsProps {
  mediaStatus: string;
  wsStatus: string;
  iceConnectionState: string;
  audioLevel: number;
}

export const VoiceStatusIndicators: React.FC<VoiceStatusIndicatorsProps> = ({
  mediaStatus, wsStatus, iceConnectionState, audioLevel
}) => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
    <div className="flex items-center space-x-2">
      <span className="font-medium">Media:</span>
      <Badge variant={mediaStatus === 'granted' ? 'default' : 'secondary'}>{mediaStatus}</Badge>
    </div>
    <div className="flex items-center space-x-2">
      <span className="font-medium">WebSocket:</span>
      <Badge variant={wsStatus === 'open' ? 'default' : 'secondary'}>{wsStatus}</Badge>
    </div>
    <div className="flex items-center space-x-2">
      <span className="font-medium">ICE:</span>
      <Badge variant={iceConnectionState === 'connected' ? 'default' : 'secondary'}>{iceConnectionState}</Badge>
    </div>
    <div className="flex items-center space-x-2">
      <span className="font-medium">Audio:</span>
      <div className="w-12 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-green-500 transition-all duration-100"
          style={{ width: `${audioLevel * 100}%` }}
        />
      </div>
    </div>
  </div>
);