import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Info } from 'lucide-react';

const DashboardSection = () => {
  return (
    <div className="space-y-6">
      <Alert>
        <Info size={16} />
        <AlertDescription>
          La personnalisation du dashboard sera disponible prochainement.
          Vous pourrez choisir quels widgets afficher et leur disposition.
        </AlertDescription>
      </Alert>
      <Card>
        <CardContent className="pt-6">
          <p className="text-gray-600">Fonctionnalité en cours de développement...</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardSection;