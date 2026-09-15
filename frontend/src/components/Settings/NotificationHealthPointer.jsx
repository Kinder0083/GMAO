import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCircle, AlertTriangle, XCircle, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import api from '../../services/api';

const STATUS_META = {
  ok: { icon: CheckCircle, color: 'text-green-600', label: 'Fonctionnel' },
  warning: { icon: AlertTriangle, color: 'text-amber-500', label: 'Avertissement' },
  error: { icon: XCircle, color: 'text-red-600', label: 'En erreur' },
  unknown: { icon: Bell, color: 'text-gray-400', label: 'Statut inconnu' }
};

const NotificationHealthPointer = () => {
  const navigate = useNavigate();
  const [overall, setOverall] = useState('unknown');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/health/notifications')
      .then(res => setOverall(res.data?.overall || 'unknown'))
      .catch(() => setOverall('unknown'))
      .finally(() => setLoading(false));
  }, []);

  const meta = STATUS_META[overall] || STATUS_META.unknown;
  const StatusIcon = meta.icon;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notifications (push, cloche, email)
        </CardTitle>
        <CardDescription>
          Diagnostic complet des canaux de notification (abonnements push, jetons mobiles, historique de livraison)
          disponible dans Santé Système.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <StatusIcon className={`h-5 w-5 ${meta.color}`} />
            <span className={`text-sm font-medium ${meta.color}`}>
              {loading ? 'Vérification...' : meta.label}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={() => navigate('/system-health')}
          >
            Ouvrir Santé Système
            <ExternalLink className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default NotificationHealthPointer;
