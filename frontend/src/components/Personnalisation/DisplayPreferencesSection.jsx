import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { usePreferences } from '../../contexts/PreferencesContext';
import { useToast } from '../../hooks/use-toast';

const DisplayPreferencesSection = () => {
  const { preferences, updatePreferences } = usePreferences();
  const { toast } = useToast();
  const [localPrefs, setLocalPrefs] = useState(preferences || {});

  useEffect(() => {
    if (preferences) {
      setLocalPrefs(preferences);
    }
  }, [preferences]);

  const handleChange = async (field, value) => {
    setLocalPrefs({ ...localPrefs, [field]: value });
    try {
      await updatePreferences({ [field]: value });
      toast({ title: 'Succès', description: 'Préférences mises à jour' });
    } catch (error) {
      toast({ title: 'Erreur', description: 'Erreur de mise à jour', variant: 'destructive' });
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div>
            <Label>Page d'accueil par défaut</Label>
            <Select value={localPrefs.default_home_page} onValueChange={(v) => handleChange('default_home_page', v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="/dashboard">Tableau de bord</SelectItem>
                <SelectItem value="/work-orders">Ordres de travail</SelectItem>
                <SelectItem value="/assets">Équipements</SelectItem>
                <SelectItem value="/inventory">Inventaire</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Format de date</Label>
              <Select value={localPrefs.date_format} onValueChange={(v) => handleChange('date_format', v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                  <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                  <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Format d'heure</Label>
              <Select value={localPrefs.time_format} onValueChange={(v) => handleChange('time_format', v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="24h">24 heures</SelectItem>
                  <SelectItem value="12h">12 heures (AM/PM)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Devise</Label>
              <Select value={localPrefs.currency} onValueChange={(v) => handleChange('currency', v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="€">Euro (€)</SelectItem>
                  <SelectItem value="$">Dollar ($)</SelectItem>
                  <SelectItem value="£">Livre (£)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DisplayPreferencesSection;