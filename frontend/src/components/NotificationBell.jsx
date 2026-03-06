import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Check, Clock, AlertTriangle, Gift, Crown, X, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ICON_MAP = {
  'clock': Clock,
  'alert': AlertTriangle,
  'alert-triangle': AlertTriangle,
  'gift': Gift,
  'crown': Crown,
};

const PRIORITY_COLORS = {
  'critical': 'bg-red-500',
  'high': 'bg-orange-500',
  'medium': 'bg-yellow-500',
  'low': 'bg-blue-500'
};

function NotificationItem({ notification, onMarkRead }) {
  const IconComponent = ICON_MAP[notification.icon] || Bell;
  const priorityColor = PRIORITY_COLORS[notification.priority] || 'bg-gray-500';
  
  return (
    <div className={`p-4 border-b last:border-b-0 hover:bg-accent/50 transition-colors ${!notification.read ? 'bg-blue-50/50 dark:bg-blue-900/20' : ''}`}>
      <div className="flex gap-3">
        <div className={`p-2 rounded-full ${priorityColor} text-white flex-shrink-0`}>
          <IconComponent className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-semibold text-sm">{notification.title}</h4>
            {!notification.read && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 w-6 p-0"
                onClick={() => onMarkRead(notification.id)}
              >
                <Check className="w-3 h-3" />
              </Button>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-muted-foreground">
              {new Date(notification.created_at).toLocaleDateString('ro-RO')}
            </span>
            <Link to={notification.action_url}>
              <Button variant="link" size="sm" className="h-auto p-0 text-xs">
                {notification.action_text}
                <ChevronRight className="w-3 h-3 ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function NotificationBell() {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    if (user && token) {
      fetchUnreadCount();
      // Poll every 60 seconds
      const interval = setInterval(fetchUnreadCount, 60000);
      return () => clearInterval(interval);
    }
  }, [user, token]);

  useEffect(() => {
    // Close dropdown when clicking outside
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const res = await fetch(`${API_URL}/api/notifications/count`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error fetching notification count:', error);
    }
  };

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/notifications?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const res = await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setNotifications(prev => 
          prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const res = await fetch(`${API_URL}/api/notifications/read-all`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const handleToggle = () => {
    if (!isOpen) {
      fetchNotifications();
    }
    setIsOpen(!isOpen);
  };

  if (!user) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      <Button 
        variant="ghost" 
        size="sm" 
        className="relative"
        onClick={handleToggle}
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <Badge 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center bg-red-500 text-white text-xs"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Button>

      {isOpen && (
        <Card className="absolute right-0 top-full mt-2 w-80 sm:w-96 z-50 shadow-lg max-h-[70vh] overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="font-semibold">Notificări</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                  <Check className="w-4 h-4 mr-1" />
                  Citește toate
                </Button>
              )}
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => setIsOpen(false)}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          <div className="overflow-y-auto max-h-[50vh]">
            {loading ? (
              <div className="p-8 text-center text-muted-foreground">
                Se încarcă...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <Bell className="w-12 h-12 mx-auto mb-3 opacity-20" />
                <p>Nu ai notificări noi</p>
              </div>
            ) : (
              notifications.map(notification => (
                <NotificationItem 
                  key={notification.id} 
                  notification={notification}
                  onMarkRead={markAsRead}
                />
              ))
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

// Export a simple banner component for critical notifications
export function CriticalNotificationBanner() {
  const { user, token } = useAuth();
  const [notification, setNotification] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (user && token) {
      fetchCriticalNotification();
    }
  }, [user, token]);

  const fetchCriticalNotification = async () => {
    try {
      const res = await fetch(`${API_URL}/api/notifications?unread_only=true&limit=1`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        // Show only critical/high priority notifications
        const critical = data.find(n => n.priority === 'critical' || n.priority === 'high');
        setNotification(critical || null);
      }
    } catch (error) {
      console.error('Error fetching critical notification:', error);
    }
  };

  if (!notification || dismissed) return null;

  const IconComponent = ICON_MAP[notification.icon] || AlertTriangle;
  const isCritical = notification.priority === 'critical';

  return (
    <div className={`${isCritical ? 'bg-red-600' : 'bg-orange-500'} text-white py-3 px-4`}>
      <div className="container mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <IconComponent className="w-5 h-5 flex-shrink-0" />
          <div>
            <span className="font-semibold">{notification.title}</span>
            <span className="hidden sm:inline ml-2 opacity-90">- {notification.message}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to={notification.action_url}>
            <Button size="sm" variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-0">
              {notification.action_text}
            </Button>
          </Link>
          <Button 
            size="sm" 
            variant="ghost" 
            className="text-white hover:bg-white/20 h-8 w-8 p-0"
            onClick={() => setDismissed(true)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
