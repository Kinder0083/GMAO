import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { AlertTriangle, Save, Trash2, X, FileWarning } from 'lucide-react';

const GitConflictDialog = ({ open, onClose, conflictData, onResolve }) => {
  const { modified_files = [] } = conflictData || {};

  const handleResolve = (strategy) => {
    onResolve(strategy);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="bg-orange-100 rounded-full p-2">
              <AlertTriangle className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <DialogTitle className="text-xl">Modifications locales détectées</DialogTitle>
              <DialogDescription className="mt-1">
                Des modifications ont été faites sur votre serveur et pourraient être écrasées
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          {/* Liste des fichiers modifiés */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <FileWarning className="h-4 w-4 text-orange-600" />
              Fichiers modifiés ({modified_files.length})
            </h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {modified_files.map((file, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <div className="bg-orange-200 text-orange-800 px-2 py-0.5 rounded text-xs font-mono">
                    {file.status}
                  </div>
                  <span className="text-gray-700 font-mono text-xs">{file.file}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Explication */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <strong>Que faire ?</strong> Vous avez 3 options pour gérer ces modifications avant de continuer la mise à jour :
            </p>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-col gap-3">
          {/* Option 1 : Écraser */}
          <Button
            onClick={() => handleResolve('reset')}
            variant="destructive"
            className="w-full justify-start"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            <div className="text-left flex-1">
              <div className="font-semibold">Écraser mes modifications</div>
              <div className="text-xs font-normal opacity-90">
                Supprimer mes changements et appliquer la mise à jour (recommandé si les modifications ne sont pas importantes)
              </div>
            </div>
          </Button>

          {/* Option 2 : Sauvegarder */}
          <Button
            onClick={() => handleResolve('stash')}
            variant="outline"
            className="w-full justify-start border-green-300 hover:bg-green-50"
          >
            <Save className="h-4 w-4 mr-2 text-green-600" />
            <div className="text-left flex-1">
              <div className="font-semibold">Sauvegarder puis mettre à jour</div>
              <div className="text-xs font-normal text-gray-600">
                Sauvegarder temporairement mes modifications (git stash) puis appliquer la mise à jour
              </div>
            </div>
          </Button>

          {/* Option 3 : Annuler */}
          <Button
            onClick={() => handleResolve('abort')}
            variant="outline"
            className="w-full justify-start"
          >
            <X className="h-4 w-4 mr-2" />
            <div className="text-left flex-1">
              <div className="font-semibold">Annuler la mise à jour</div>
              <div className="text-xs font-normal text-gray-600">
                Garder mes modifications et ne pas faire la mise à jour maintenant
              </div>
            </div>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default GitConflictDialog;
