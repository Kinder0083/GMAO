import {
  ClipboardList,
  Wrench,
  Clock,
  Package,
  AlertTriangle,
  BarChart3,
  Calendar,
  TrendingUp,
  Users,
  Zap,
  CalendarClock,
  FileText,
  History,
  Bell,
  AlertCircle,
  CheckCircle2,
  Timer,
} from 'lucide-react';

/**
 * Catalogue unique des widgets du tableau de bord : source de verite partagee
 * entre la page Personnalisation (activer/desactiver, ordre) et le Dashboard
 * lui-meme (liste par defaut, libelles du bouton "Ajouter un widget").
 *
 * Avant cette consolidation, cette meme liste existait en 3 copies
 * independantes dans Dashboard.jsx (deja desynchronisees), en plus de
 * celle-ci - meme famille de bug que les listes de menu deja corrigees.
 */
export const AVAILABLE_WIDGETS = [
  // Widgets principaux du dashboard
  { id: 'work_orders_active', name: 'Ordres de travail actifs', icon: ClipboardList, description: 'Nombre d\'ordres en cours', enabled: true, category: 'principal' },
  { id: 'equipment_maintenance', name: 'Équipements en maintenance', icon: Wrench, description: 'Équipements actuellement en maintenance', enabled: true, category: 'principal' },
  { id: 'overdue_tasks', name: 'Tâches en retard', icon: Clock, description: 'Tâches dépassant l\'échéance', enabled: true, category: 'principal' },
  { id: 'low_stock', name: 'Stock bas', icon: Package, description: 'Articles d\'inventaire en rupture', enabled: true, category: 'principal' },
  { id: 'recent_incidents', name: 'Incidents récents', icon: AlertTriangle, description: 'Incidents signalés récemment', enabled: true, category: 'principal' },
  { id: 'maintenance_stats', name: 'Statistiques de maintenance', icon: BarChart3, description: 'Graphiques et métriques', enabled: true, category: 'principal' },
  { id: 'upcoming_maintenance', name: 'Maintenances à venir', icon: Calendar, description: 'Planifications préventives', enabled: true, category: 'principal' },
  { id: 'performance_metrics', name: 'Métriques de performance', icon: TrendingUp, description: 'KPIs et indicateurs', enabled: false, category: 'principal' },
  { id: 'team_activity', name: 'Activité d\'équipe', icon: Users, description: 'Tâches par technicien', enabled: false, category: 'principal' },
  { id: 'quick_actions', name: 'Actions rapides', icon: Zap, description: 'Raccourcis vers actions courantes', enabled: true, category: 'principal' },

  // Demandes d'arrêt et Reports
  { id: 'demandes_arret_pending', name: 'Demandes d\'arrêt en attente', icon: Bell, description: 'Nombre de demandes en attente de validation', enabled: true, category: 'demandes' },
  { id: 'demandes_arret_stats', name: 'Statistiques des demandes', icon: FileText, description: 'Vue d\'ensemble des demandes d\'arrêt', enabled: true, category: 'demandes' },
  { id: 'reports_pending', name: 'Reports en attente', icon: CalendarClock, description: 'Demandes de report en attente', enabled: true, category: 'demandes' },
  { id: 'reports_stats', name: 'Statistiques des reports', icon: History, description: 'Métriques sur les reports de maintenance', enabled: false, category: 'demandes' },

  // Planning et Équipements
  { id: 'planning_mprev_summary', name: 'Résumé Planning M.Prev', icon: Calendar, description: 'Vue résumée du planning de maintenance préventive', enabled: true, category: 'planning' },
  { id: 'equipment_status_overview', name: 'Vue d\'ensemble statuts équipements', icon: Wrench, description: 'Répartition des statuts des équipements', enabled: true, category: 'planning' },
  { id: 'equipment_alerts', name: 'Alertes équipements', icon: AlertCircle, description: 'Équipements en alerte (sous-équipement hors service)', enabled: true, category: 'planning' },
  { id: 'recent_status_changes', name: 'Changements de statut récents', icon: History, description: 'Historique des derniers changements de statut', enabled: false, category: 'planning' },

  // Demandes d'intervention et temps
  { id: 'di_en_attente', name: 'DI en attente', icon: Bell, description: 'Demandes d\'intervention non traitees', enabled: true, category: 'interventions' },
  { id: 'di_temps_reponse', name: 'Temps reponse DI', icon: CalendarClock, description: 'Temps moyen de traitement des DI', enabled: true, category: 'interventions' },
  { id: 'ecart_temps', name: 'Ecart Temps Est./Reel', icon: Timer, description: 'Écart entre temps estimé et temps réel passé sur les OT', enabled: true, category: 'interventions' },
  { id: 'charge_maintenance', name: 'Charge OT restante', icon: Clock, description: 'Charge de travail restante répartie sur l\'équipe maintenance', enabled: true, category: 'interventions' },

  // Widget résumé global
  { id: 'global_summary', name: 'Résumé global', icon: CheckCircle2, description: 'Vue d\'ensemble de l\'état du système', enabled: true, category: 'global' },
];

/**
 * Libellés id -> nom affiche, derives du catalogue (utilise par le bouton
 * "Ajouter un widget"). Note : la liste des widgets presents par defaut sur
 * le tableau de bord d'un nouvel utilisateur (Dashboard.jsx) reste une
 * selection deliberement plus restreinte que "tous les widgets actives par
 * defaut dans Personnalisation" (le champ `enabled` ci-dessus) - ce sont deux
 * notions distinctes, volontairement non fusionnees ici.
 */
export const WIDGET_LABELS = Object.fromEntries(AVAILABLE_WIDGETS.map(w => [w.id, w.name]));
