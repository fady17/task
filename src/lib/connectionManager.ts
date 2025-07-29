import { appEventBus } from '@/lib/eventBus';
import { API_CONFIG, PEER_CONNECTION_CONFIG } from '@/config';

class ConnectionManager {
  private pc: RTCPeerConnection | null = null;
  private dc: RTCDataChannel | null = null;
  private ws: WebSocket | null = null;
  private connectionTimeout: NodeJS.Timeout | null = null;
  private isConnecting: boolean = false;
  public onStatusChange: (status: string) => void = () => {};

  public connect() {
    if (this.isConnecting) {
      return;
    }
    
    if (this.ws && this.ws.readyState < 2) { 
      return; 
    }

    this.isConnecting = true;
    this.onStatusChange('connecting');
    
    this.connectionTimeout = setTimeout(() => {
      this.cleanup();
      this.onStatusChange('error');
    }, 20000);

    try {
      this.ws = new WebSocket(API_CONFIG.WEBSOCKET_URL);
    } catch (error) {
      console.error('ConnectionManager: WebSocket creation failed:', error);
      this.cleanup();
      this.onStatusChange('error');
      return;
    }

    this.ws.onopen = () => {
      try {
        this.pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);

        this.pc.onconnectionstatechange = () => {
          const state = this.pc?.connectionState;
          
          if (state === 'failed') {
            console.error('ConnectionManager: RTCPeerConnection failed');
            this.cleanup();
            this.onStatusChange('error');
          } else if (state === 'disconnected' || state === 'closed') {
            this.cleanup();
            this.onStatusChange('disconnected');
          }
        };

        this.pc.oniceconnectionstatechange = () => {
          const iceState = this.pc?.iceConnectionState;
          
          if (iceState === 'failed' || iceState === 'disconnected') {
            console.error('ConnectionManager: ICE connection failed/disconnected');
            this.cleanup();
            this.onStatusChange('error');
          }
        };

        this.pc.onicegatheringstatechange = () => {
          // ICE gathering state changes
        };

        this.dc = this.pc.createDataChannel('chat');
        
        this.dc.onopen = () => {
          this.clearTimeout();
          this.isConnecting = false;
          this.onStatusChange('connected');
        };
        
        this.dc.onclose = () => {
          this.cleanup();
          this.onStatusChange('disconnected');
        };
        
        this.dc.onerror = (error) => {
          console.error('ConnectionManager: DataChannel error:', error);
          this.cleanup();
          this.onStatusChange('error');
        };
        
        // ENHANCED MESSAGE HANDLING
        this.dc.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Handle all types of state changes
            if (data.type === 'state_change' || data.type === 'force_state_change') {
              appEventBus.emit('state_change', { 
                resource: data.resource,
                action: data.action,
                timestamp: data.timestamp
              });
            } else if (data.type === 'chat_message') {
              appEventBus.emit('chat_message', data.content);
            }
            
            // FALLBACK: If no specific type, treat as state change
            else {
              appEventBus.emit('state_change', { resource: 'todos' });
            }
            
          } catch (e) {
            // Treat non-JSON messages as chat messages
            appEventBus.emit('chat_message', event.data);
          }
        };

        this.pc.createOffer()
          .then(offer => {
            return this.pc!.setLocalDescription(offer);
          })
          .then(() => {
            if (this.ws?.readyState === WebSocket.OPEN) {
              this.ws.send(JSON.stringify({ 
                type: 'offer', 
                sdp: this.pc!.localDescription?.sdp 
              }));
            } else {
              throw new Error('WebSocket not ready when sending offer');
            }
          })
          .catch(error => {
            console.error('ConnectionManager: Offer creation/sending failed:', error);
            this.cleanup();
            this.onStatusChange('error');
          });
          
      } catch (error) {
        console.error('ConnectionManager: RTCPeerConnection setup failed:', error);
        this.cleanup();
        this.onStatusChange('error');
      }
    };

    this.ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'answer' && this.pc) {
          await this.pc.setRemoteDescription(new RTCSessionDescription(data));
        }
      } catch (error) {
        console.error('ConnectionManager: WebSocket message handling failed:', error);
        this.cleanup();
        this.onStatusChange('error');
      }
    };

    this.ws.onerror = (error) => {
      console.error('ConnectionManager: WebSocket error:', error);
      this.cleanup();
      this.onStatusChange('error');
    };
    
    this.ws.onclose = (event) => {
      this.cleanup();
      
      if (event.code === 1000) {
        this.onStatusChange('disconnected');
      } else {
        this.onStatusChange('error');
      }
    };
  }

  private clearTimeout() {
    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
  }

  private cleanup() {
    this.isConnecting = false;
    this.clearTimeout();
  }

  public sendMessage(message: string) {
    if (this.dc?.readyState === 'open') {
      this.dc.send(message);
      return true;
    } else {
      console.warn('ConnectionManager: Cannot send message, DataChannel not open. State:', this.dc?.readyState);
      return false;
    }
  }

  public disconnect() {
    this.cleanup();
    this.pc?.close();
    this.ws?.close();
  }

  public reconnect() {
    this.disconnect();
    setTimeout(() => this.connect(), 1000);
  }
}

export const connectionManager = new ConnectionManager();

// import { appEventBus } from '@/lib/eventBus';
// import { API_CONFIG, PEER_CONNECTION_CONFIG } from '@/config';

// class ConnectionManager {
//   private pc: RTCPeerConnection | null = null;
//   private dc: RTCDataChannel | null = null;
//   private ws: WebSocket | null = null;
//   private connectionTimeout: NodeJS.Timeout | null = null;
//   private isConnecting: boolean = false;
//   public onStatusChange: (status: string) => void = () => {};

//   public connect() {
//     console.log('🔌 ConnectionManager: Starting connection...');
    
//     if (this.isConnecting) {
//       console.log('🔌 ConnectionManager: Already connecting, skipping...');
//       return;
//     }
    
//     if (this.ws && this.ws.readyState < 2) { 
//       console.log('🔌 ConnectionManager: Already connected/connecting');
//       return; 
//     }

//     this.isConnecting = true;
//     this.onStatusChange('connecting');
    
//     this.connectionTimeout = setTimeout(() => {
//       console.log('🔌 ConnectionManager: Connection timeout after 20s');
//       this.cleanup();
//       this.onStatusChange('error');
//     }, 20000);

//     try {
//       console.log('🔌 ConnectionManager: Creating WebSocket connection to:', API_CONFIG.WEBSOCKET_URL);
//       this.ws = new WebSocket(API_CONFIG.WEBSOCKET_URL);
//     } catch (error) {
//       console.error('🔌 ConnectionManager: WebSocket creation failed:', error);
//       this.cleanup();
//       this.onStatusChange('error');
//       return;
//     }

//     this.ws.onopen = () => {
//       console.log('🔌 ConnectionManager: WebSocket connected');
      
//       try {
//         this.pc = new RTCPeerConnection(PEER_CONNECTION_CONFIG);
//         console.log('🔌 ConnectionManager: RTCPeerConnection created with config:', PEER_CONNECTION_CONFIG);

//         this.pc.onconnectionstatechange = () => {
//           const state = this.pc?.connectionState;
//           console.log('🔌 ConnectionManager: RTCPeerConnection state changed to:', state);
          
//           if (state === 'failed') {
//             console.error('🔌 ConnectionManager: RTCPeerConnection failed');
//             this.cleanup();
//             this.onStatusChange('error');
//           } else if (state === 'disconnected' || state === 'closed') {
//             console.log('🔌 ConnectionManager: RTCPeerConnection disconnected/closed');
//             this.cleanup();
//             this.onStatusChange('disconnected');
//           }
//         };

//         this.pc.oniceconnectionstatechange = () => {
//           const iceState = this.pc?.iceConnectionState;
//           console.log('🔌 ConnectionManager: ICE connection state:', iceState);
          
//           if (iceState === 'failed' || iceState === 'disconnected') {
//             console.error('🔌 ConnectionManager: ICE connection failed/disconnected');
//             this.cleanup();
//             this.onStatusChange('error');
//           }
//         };

//         this.pc.onicegatheringstatechange = () => {
//           console.log('🔌 ConnectionManager: ICE gathering state:', this.pc?.iceGatheringState);
//         };

//         this.dc = this.pc.createDataChannel('chat');
//         console.log('🔌 ConnectionManager: DataChannel created');
        
//         this.dc.onopen = () => {
//           console.log('🔌 ConnectionManager: DataChannel opened - CONNECTED!');
//           this.clearTimeout();
//           this.isConnecting = false;
//           this.onStatusChange('connected');
//         };
        
//         this.dc.onclose = () => {
//           console.log('🔌 ConnectionManager: DataChannel closed');
//           this.cleanup();
//           this.onStatusChange('disconnected');
//         };
        
//         this.dc.onerror = (error) => {
//           console.error('🔌 ConnectionManager: DataChannel error:', error);
//           this.cleanup();
//           this.onStatusChange('error');
//         };
        
//         // ENHANCED MESSAGE HANDLING
//         this.dc.onmessage = (event) => {
//           console.log('📨 Received DataChannel message:', event.data);
          
//           try {
//             const data = JSON.parse(event.data);
//             console.log('📨 Parsed message:', data);
            
//             // Handle all types of state changes
//             if (data.type === 'state_change' || data.type === 'force_state_change') {
//               console.log('📡 Broadcasting state change:', data.resource);
//               appEventBus.emit('state_change', { 
//                 resource: data.resource,
//                 action: data.action,
//                 timestamp: data.timestamp
//               });
//             } else if (data.type === 'chat_message') {
//               console.log('💬 Broadcasting chat message');
//               appEventBus.emit('chat_message', data.content);
//             }
            
//             // FALLBACK: If no specific type, treat as state change
//             else {
//               console.log('📡 Fallback: Broadcasting generic state change');
//               appEventBus.emit('state_change', { resource: 'todos' });
//             }
            
//           } catch (e) {
//             console.log('📨 Raw message (not JSON):', event.data);
//             // Treat non-JSON messages as chat messages
//             appEventBus.emit('chat_message', event.data);
//           }
//         };

//         this.pc.createOffer()
//           .then(offer => {
//             console.log('🔌 ConnectionManager: Offer created');
//             return this.pc!.setLocalDescription(offer);
//           })
//           .then(() => {
//             console.log('🔌 ConnectionManager: Local description set, sending offer');
//             if (this.ws?.readyState === WebSocket.OPEN) {
//               this.ws.send(JSON.stringify({ 
//                 type: 'offer', 
//                 sdp: this.pc!.localDescription?.sdp 
//               }));
//             } else {
//               throw new Error('WebSocket not ready when sending offer');
//             }
//           })
//           .catch(error => {
//             console.error('🔌 ConnectionManager: Offer creation/sending failed:', error);
//             this.cleanup();
//             this.onStatusChange('error');
//           });
          
//       } catch (error) {
//         console.error('🔌 ConnectionManager: RTCPeerConnection setup failed:', error);
//         this.cleanup();
//         this.onStatusChange('error');
//       }
//     };

//     this.ws.onmessage = async (event) => {
//       try {
//         const data = JSON.parse(event.data);
//         console.log('🔌 ConnectionManager: Received WebSocket message:', data.type);
        
//         if (data.type === 'answer' && this.pc) {
//           console.log('🔌 ConnectionManager: Setting remote description');
//           await this.pc.setRemoteDescription(new RTCSessionDescription(data));
//         }
//       } catch (error) {
//         console.error('🔌 ConnectionManager: WebSocket message handling failed:', error);
//         this.cleanup();
//         this.onStatusChange('error');
//       }
//     };

//     this.ws.onerror = (error) => {
//       console.error('🔌 ConnectionManager: WebSocket error:', error);
//       this.cleanup();
//       this.onStatusChange('error');
//     };
    
//     this.ws.onclose = (event) => {
//       console.log('🔌 ConnectionManager: WebSocket closed:', event.code, event.reason);
//       this.cleanup();
      
//       if (event.code === 1000) {
//         this.onStatusChange('disconnected');
//       } else {
//         this.onStatusChange('error');
//       }
//     };
//   }

//   private clearTimeout() {
//     if (this.connectionTimeout) {
//       clearTimeout(this.connectionTimeout);
//       this.connectionTimeout = null;
//     }
//   }

//   private cleanup() {
//     this.isConnecting = false;
//     this.clearTimeout();
//   }

//   public sendMessage(message: string) {
//     console.log('📤 Attempting to send message:', message);
    
//     if (this.dc?.readyState === 'open') {
//       this.dc.send(message);
//       console.log('✅ Message sent successfully');
//       return true;
//     } else {
//       console.warn('🔌 ConnectionManager: Cannot send message, DataChannel not open. State:', this.dc?.readyState);
//       return false;
//     }
//   }

//   public disconnect() {
//     console.log('🔌 ConnectionManager: Disconnecting...');
//     this.cleanup();
//     this.pc?.close();
//     this.ws?.close();
//   }

//   public reconnect() {
//     console.log('🔌 ConnectionManager: Reconnecting...');
//     this.disconnect();
//     setTimeout(() => this.connect(), 1000);
//   }
// }

// export const connectionManager = new ConnectionManager();

