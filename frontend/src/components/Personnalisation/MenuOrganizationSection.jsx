import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Info } from 'lucide-react';

const MenuOrganizationSection = () => {
  return (
    <div className="space-y-6">
      <Alert>
        <Info size={16} />
        <AlertDescription>
          La fonctionnalité de réorganisation des menus par drag & drop sera disponible prochainement.
          Pour l'instant, l'ordre des menus est défini par défaut.
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

export default MenuOrganizationSection;