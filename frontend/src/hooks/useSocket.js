import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from '../contexts/AuthContext';

export const useSocket = () => {
  const { user, token } = useAuth();
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (user && token) {
      // Initialize socket connection
      socketRef.current = io('/', {
        auth: {
          token: token
        },
        transports: ['websocket', 'polling']
      });

      const socket = socketRef.current;

      // Connection event handlers
      socket.on('connect', () => {
        console.log('Connected to server');
        setIsConnected(true);
        
        // Join user-specific room
        socket.emit('join_room', { room: `user_${user.id}` });
      });

      socket.on('disconnect', () => {
        console.log('Disconnected from server');
        setIsConnected(false);
      });

      socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setIsConnected(false);
      });

      // Task-related events
      socket.on('task_created', (data) => {
        console.log('New task created:', data);
        addNotification({
          id: Date.now(),
          type: 'task_created',
          message: `New task created: ${data.task.title}`,
          data: data.task,
          timestamp: new Date().toISOString()
        });
      });

      socket.on('task_updated', (data) => {
        console.log('Task updated:', data);
        addNotification({
          id: Date.now(),
          type: 'task_updated',
          message: `Task updated: ${data.task.title}`,
          data: data.task,
          timestamp: new Date().toISOString()
        });
      });

      socket.on('task_assigned', (data) => {
        console.log('Task assigned:', data);
        addNotification({
          id: Date.now(),
          type: 'task_assigned',
          message: `You have been assigned a new task: ${data.task.title}`,
          data: data.task,
          timestamp: new Date().toISOString()
        });
      });

      socket.on('task_status_changed', (data) => {
        console.log('Task status changed:', data);
        addNotification({
          id: Date.now(),
          type: 'task_status_changed',
          message: `Task status changed: ${data.task.title} is now ${data.task.status}`,
          data: data.task,
          timestamp: new Date().toISOString()
        });
      });

      // Cleanup on unmount
      return () => {
        if (socket) {
          socket.disconnect();
        }
      };
    }
  }, [user, token]);

  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Keep last 10 notifications
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const emitTaskEvent = (eventName, data) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit(eventName, data);
    }
  };

  const joinRoom = (room) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('join_room', { room });
    }
  };

  const leaveRoom = (room) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('leave_room', { room });
    }
  };

  return {
    socket: socketRef.current,
    isConnected,
    notifications,
    removeNotification,
    clearNotifications,
    emitTaskEvent,
    joinRoom,
    leaveRoom
  };
};

