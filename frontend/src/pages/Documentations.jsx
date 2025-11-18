import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Plus, FolderOpen, Edit, Trash2, FileText, Search } from 'lucide-react';
import { documentationsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { useConfirmDialog } from '../components/ui/confirm-dialog';
import { formatErrorMessage } from '../utils/errorFormatter';

const POLE_COLORS = {
  MAINTENANCE: '#f97316',
  PRODUCTION: '#3b82f6',
  QHSE: '#22c55e',
  LOGISTIQUE: '#a855f7',
  LABO: '#06b6d4',
  ADV: '#ec4899',
  INDUS: '#f59e0b',
  DIRECTION: '#ef4444',
  RH: '#8b5cf6',
  AUTRE: '#6b7280'
};

const POLE_ICONS = {
  MAINTENANCE: '🔧',
  PRODUCTION: '🏭',
  QHSE: '🛡️',
  LOGISTIQUE: '📦',
  LABO: '🧪',
  ADV: '💼',
  INDUS: '⚙️',
  DIRECTION: '👔',
  RH: '👥',
  AUTRE: '📁'
};

function Documentations() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { confirm, ConfirmDialog } = useConfirmDialog();
  const [poles, setPoles] = useState([]);
  const [filteredPoles, setFilteredPoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openForm, setOpenForm] = useState(false);
  const [selectedPole, setSelectedPole] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState({
    nom: '',
    pole: 'AUTRE',
    description: '',
    responsable: '',
    couleur: '#3b82f6',
    icon: 'Folder'
  });

  useEffect(() => {
    loadPoles();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = poles.filter(pole =>
        pole.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        pole.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPoles(filtered);
    } else {
      setFilteredPoles(poles);
    }
  }, [searchTerm, poles]);

  const loadPoles = async () => {
    try {
      setLoading(true);
      const data = await documentationsAPI.getPoles();
      setPoles(data);
      setFilteredPoles(data);
    } catch (error) {
      console.error('Erreur chargement pôles:', error);
      toast({
        title: 'Erreur',
        description: formatErrorMessage(error, 'Erreur lors du chargement'),
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedPole(null);
    setFormData({
      nom: '',
      pole: 'AUTRE',
      description: '',
      responsable: '',
      couleur: '#3b82f6',
      icon: 'Folder'
    });
    setOpenForm(true);
  };

  const handleEdit = (pole) => {
    setSelectedPole(pole);
    setFormData({
      nom: pole.nom || '',
      pole: pole.pole || 'AUTRE',
      description: pole.description || '',
      responsable: pole.responsable || '',
      couleur: pole.couleur || '#3b82f6',
      icon: pole.icon || 'Folder'
    });
    setOpenForm(true);
  };

  const handleDelete = (poleId) => {
    confirm({
      title: 'Supprimer le pôle',
      description: 'Êtes-vous sûr de vouloir supprimer ce pôle de service ? Cette action est irréversible.',
      confirmText: 'Supprimer',
      cancelText: 'Annuler',
      variant: 'destructive',
      onConfirm: async () => {
        try {
          await documentationsAPI.deletePole(poleId);
          toast({ title: 'Succès', description: 'Pôle supprimé' });
          loadPoles();
        } catch (error) {
          toast({
            title: 'Erreur',
            description: formatErrorMessage(error, 'Erreur lors de la suppression'),
            variant: 'destructive'
          });
        }
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Mettre à jour la couleur selon le pôle sélectionné
      const poleData = {
        ...formData,
        couleur: POLE_COLORS[formData.pole] || formData.couleur
      };

      if (selectedPole) {
        await documentationsAPI.updatePole(selectedPole.id, poleData);
        toast({ title: 'Succès', description: 'Pôle mis à jour' });
      } else {
        await documentationsAPI.createPole(poleData);
        toast({ title: 'Succès', description: 'Pôle créé' });
      }
      setOpenForm(false);
      loadPoles();
    } catch (error) {
      toast({
        title: 'Erreur',
        description: formatErrorMessage(error, 'Erreur lors de l\'enregistrement'),
        variant: 'destructive'
      });
    }
  };

  const handlePoleClick = (poleId) => {
    navigate(`/documentations/${poleId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Chargement...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Documentations</h1>
          <p className="text-gray-500">Gestion des pôles de service et documents</p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Nouveau Pôle
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Rechercher un pôle..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Pôles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPoles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <FolderOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500">Aucun pôle de service trouvé</p>
            <Button onClick={handleCreate} className="mt-4">
              Créer le premier pôle
            </Button>
          </div>
        ) : (
          filteredPoles.map((pole) => (
            <Card
              key={pole.id}
              className="hover:shadow-lg transition-shadow cursor-pointer group"
              style={{ borderLeftWidth: '4px', borderLeftColor: pole.couleur || POLE_COLORS[pole.pole] }}
            >
              <CardHeader
                className="pb-3"
                onClick={() => handlePoleClick(pole.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                      style={{ backgroundColor: `${pole.couleur || POLE_COLORS[pole.pole]}20` }}
                    >
                      {POLE_ICONS[pole.pole] || '📁'}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{pole.nom}</CardTitle>
                      <p className="text-sm text-gray-500">{pole.pole}</p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent onClick={() => handlePoleClick(pole.id)}>
                {pole.description && (
                  <p className="text-sm text-gray-600 mb-3">{pole.description}</p>
                )}
                {pole.responsable && (
                  <p className="text-xs text-gray-500">
                    Responsable : <span className="font-medium">{pole.responsable}</span>
                  </p>
                )}
              </CardContent>
              <div className="px-6 pb-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit(pole);
                  }}
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(pole.id);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Form Dialog */}
      <Dialog open={openForm} onOpenChange={setOpenForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedPole ? 'Modifier' : 'Nouveau'} Pôle de Service</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Nom du pôle *</Label>
                <Input
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  placeholder="ex: Service Maintenance"
                  required
                />
              </div>

              <div>
                <Label>Type de pôle *</Label>
                <Select
                  value={formData.pole}
                  onValueChange={(value) => setFormData({ ...formData, pole: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MAINTENANCE">Maintenance</SelectItem>
                    <SelectItem value="PRODUCTION">Production</SelectItem>
                    <SelectItem value="QHSE">QHSE</SelectItem>
                    <SelectItem value="LOGISTIQUE">Logistique</SelectItem>
                    <SelectItem value="LABO">Laboratoire</SelectItem>
                    <SelectItem value="ADV">ADV</SelectItem>
                    <SelectItem value="INDUS">Industrialisation</SelectItem>
                    <SelectItem value="DIRECTION">Direction</SelectItem>
                    <SelectItem value="RH">Ressources Humaines</SelectItem>
                    <SelectItem value="AUTRE">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="col-span-2">
                <Label>Description</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  placeholder="Description du pôle..."
                />
              </div>

              <div className="col-span-2">
                <Label>Responsable</Label>
                <Input
                  value={formData.responsable}
                  onChange={(e) => setFormData({ ...formData, responsable: e.target.value })}
                  placeholder="Nom du responsable"
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpenForm(false)}>
                Annuler
              </Button>
              <Button type="submit">
                {selectedPole ? 'Mettre à jour' : 'Créer'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Confirm Dialog */}
      <ConfirmDialog />
    </div>
  );
}

export default Documentations;
