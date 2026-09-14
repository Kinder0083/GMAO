import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Button } from '../ui/button';
import { usePreferences } from '../../contexts/PreferencesContext';
import { useToast } from '../../hooks/use-toast';
import { AVAILABLE_WIDGETS } from '../../constants/dashboardWidgets';

const DashboardSection = () => {
  const { preferences, updatePreferences } = usePreferences();
  const { toast } = useToast();
  const [widgets, setWidgets] = useState([]);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    // Initialiser les widgets une seule fois
    if (!initialized) {
      if (preferences?.dashboard_widgets !== undefined && preferences?.dashboard_widgets !== null) {
        // Si dashboard_widgets existe (même vide), l'utiliser
        setWidgets(preferences.dashboard_widgets);
      } else {
        // Sinon, utiliser les widgets par défaut
        const defaultWidgets = AVAILABLE_WIDGETS.filter(w => w.enabled).map(w => w.id);
        setWidgets(defaultWidgets);
      }
      setInitialized(true);
    }
  }, [preferences, initialized]);

  const isWidgetEnabled = (widgetId) => {
    return widgets.includes(widgetId);
  };

  const toggleWidget = async (widgetId) => {
    let updatedWidgets;
    if (isWidgetEnabled(widgetId)) {
      updatedWidgets = widgets.filter(id => id !== widgetId);
    } else {
      updatedWidgets = [...widgets, widgetId];
    }
    
    setWidgets(updatedWidgets);

    try {
      await updatePreferences({ dashboard_widgets: updatedWidgets });
      toast({ title: 'Succès', description: 'Widgets du dashboard mis à jour' });
    } catch (error) {
      toast({ title: 'Erreur', description: 'Erreur de mise à jour', variant: 'destructive' });
    }
  };

  const enableAll = async () => {
    const allWidgets = AVAILABLE_WIDGETS.map(w => w.id);
    setWidgets(allWidgets);
    try {
      await updatePreferences({ dashboard_widgets: allWidgets });
      toast({ title: 'Succès', description: 'Tous les widgets activés' });
    } catch (error) {
      toast({ title: 'Erreur', description: 'Erreur de mise à jour', variant: 'destructive' });
    }
  };

  const disableAll = async () => {
    setWidgets([]);
    try {
      await updatePreferences({ dashboard_widgets: [] });
      toast({ title: 'Succès', description: 'Tous les widgets désactivés' });
    } catch (error) {
      toast({ title: 'Erreur', description: 'Erreur de mise à jour', variant: 'destructive' });
    }
  };

  const resetToDefault = async () => {
    const defaultWidgets = AVAILABLE_WIDGETS.filter(w => w.enabled).map(w => w.id);
    setWidgets(defaultWidgets);
    try {
      await updatePreferences({ dashboard_widgets: defaultWidgets });
      toast({ title: 'Succès', description: 'Widgets par défaut restaurés' });
    } catch (error) {
      toast({ title: 'Erreur', description: 'Erreur de réinitialisation', variant: 'destructive' });
    }
  };

  // Grouper les widgets par catégorie
  const categories = {
    principal: { name: 'Widgets Principaux', widgets: AVAILABLE_WIDGETS.filter(w => w.category === 'principal') },
    demandes: { name: 'Demandes d\'Arrêt & Reports', widgets: AVAILABLE_WIDGETS.filter(w => w.category === 'demandes') },
    planning: { name: 'Planning & Équipements', widgets: AVAILABLE_WIDGETS.filter(w => w.category === 'planning') },
    interventions: { name: 'Demandes d\'Intervention & Temps', widgets: AVAILABLE_WIDGETS.filter(w => w.category === 'interventions') },
    global: { name: 'Résumé', widgets: AVAILABLE_WIDGETS.filter(w => w.category === 'global') }
  };

  const renderWidgetCard = (widget) => {
    const Icon = widget.icon;
    return (
      <div
        key={widget.id}
        className={`flex items-start gap-4 p-4 rounded-lg border transition-all ${
          isWidgetEnabled(widget.id)
            ? 'border-blue-300 bg-blue-50'
            : 'border-gray-200 bg-white'
        }`}
      >
        <div className={`p-2 rounded-lg ${
          isWidgetEnabled(widget.id) ? 'bg-blue-100' : 'bg-gray-100'
        }`}>
          <Icon size={24} className={isWidgetEnabled(widget.id) ? 'text-blue-600' : 'text-gray-600'} />
        </div>
        <div className="flex-1">
          <h4 className="font-medium text-sm mb-1">{widget.name}</h4>
          <p className="text-xs text-gray-500">{widget.description}</p>
        </div>
        <Switch
          checked={isWidgetEnabled(widget.id)}
          onCheckedChange={() => toggleWidget(widget.id)}
        />
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-center mb-4">
            <Label className="text-base font-semibold">Widgets du tableau de bord</Label>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={enableAll}>
                Tout activer
              </Button>
              <Button variant="outline" size="sm" onClick={disableAll}>
                Tout désactiver
              </Button>
              <Button variant="outline" size="sm" onClick={resetToDefault}>
                Par défaut
              </Button>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-6">
            Sélectionnez les widgets à afficher sur votre tableau de bord ({widgets.length} actif{widgets.length > 1 ? 's' : ''})
          </p>

          {/* Affichage par catégorie */}
          {Object.entries(categories).map(([categoryId, category]) => (
            <div key={categoryId} className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                {category.name}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {category.widgets.map(renderWidgetCard)}
              </div>
            </div>
          ))}

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>💡 Astuce :</strong> Les widgets activés apparaîtront sur votre tableau de bord.
              Désactivez les widgets que vous n'utilisez pas pour un affichage plus épuré.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardSection;