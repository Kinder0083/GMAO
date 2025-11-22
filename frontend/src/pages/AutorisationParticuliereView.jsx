import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, Download, Printer, Edit } from 'lucide-react';
import { documentationsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { formatErrorMessage } from '../utils/errorFormatter';

function AutorisationParticuliereView() {
  const { poleId, autorisationId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [autorisation, setAutorisation] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setCurrentUser(JSON.parse(userData));
    }
    loadAutorisation();
  }, [autorisationId]);

  const loadAutorisation = async () => {
    try {
      setLoading(true);
      const data = await documentationsAPI.getAutorisation(autorisationId);
      setAutorisation(data);
    } catch (error) {
      toast({
        title: 'Erreur',
        description: formatErrorMessage(error, 'Erreur lors du chargement'),
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const canEdit = () => {
    if (!currentUser || !autorisation) return false;
    if (currentUser.role === 'ADMIN') return true;
    return autorisation.created_by === currentUser.id;
  };

  const handlePrint = () => {
    const token = localStorage.getItem('token');
    const printUrl = `${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/autorisations/${autorisationId}/pdf?token=${token}`;
    const printWindow = window.open(printUrl, '_blank');
    if (printWindow) {
      printWindow.onload = () => printWindow.print();
    }
  };

  const PrecautionDisplay = ({ label, prec }) => {
    if (!prec) return null;
    const state = prec.fait ? 'FAIT' : prec.oui ? 'OUI' : prec.non ? 'NON' : 'Non défini';
    const color = prec.fait ? 'bg-green-100 text-green-800' : prec.oui ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800';
    
    return (
      <div className="flex justify-between items-center py-2 border-b">
        <span className="text-sm">{label}</span>
        <Badge className={color}>{state}</Badge>
      </div>
    );
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Chargement...</div>;
  }

  if (!autorisation) {
    return <div className="text-center text-gray-500 py-12">Autorisation non trouvée</div>;
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/documentations/${poleId}`)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Autorisation Particulière de Travaux</h1>
            <p className="text-gray-500">
              Créée le {autorisation.created_at ? new Date(autorisation.created_at).toLocaleDateString('fr-FR') : 'Date inconnue'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {canEdit() && (
            <Button variant="outline" onClick={() => navigate(`/documentations/${poleId}/autorisation/${autorisationId}/edit`)}>
              <Edit className="mr-2 h-4 w-4" />
              Modifier
            </Button>
          )}
          <Button variant="outline" onClick={handlePrint}>
            <Printer className="mr-2 h-4 w-4" />
            Imprimer
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              const token = localStorage.getItem('token');
              window.open(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/autorisations/${autorisationId}/pdf?token=${token}`, '_blank');
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            Télécharger PDF
          </Button>
        </div>
      </div>

      {/* Type de travaux */}
      <Card>
        <CardHeader>
          <CardTitle>Type de travaux</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            {autorisation.type_point_chaud && <Badge>Point chaud</Badge>}
            {autorisation.type_espace_clos && <Badge>Espace clos</Badge>}
            {autorisation.type_fouille && <Badge>Fouille</Badge>}
            {autorisation.type_autre && <Badge>Autre: {autorisation.type_autre_precision}</Badge>}
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Détail des travaux</p>
            <p className="text-base whitespace-pre-wrap mt-2">{autorisation.detail_travaux}</p>
          </div>
        </CardContent>
      </Card>

      {/* Lieu et dangers */}
      <Card>
        <CardHeader>
          <CardTitle>Lieu d'intervention et dangers</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-sm font-semibold text-gray-600">Matériel ou appareillage</p>
            <p>{autorisation.lieu_materiel_appareillage || 'Non renseigné'}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Dernier produit/fluide</p>
            <p>{autorisation.lieu_dernier_produit || 'Non renseigné'}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Dangers avoisinants</p>
            <p>{autorisation.lieu_danger_avoisinant || 'Non renseigné'}</p>
          </div>
        </CardContent>
      </Card>

      {/* Précautions */}
      <Card>
        <CardHeader>
          <CardTitle>Précautions à prendre</CardTitle>
        </CardHeader>
        <CardContent>
          <PrecautionDisplay label="Consignation matériel" prec={autorisation.prec_consignation_materiel} />
          <PrecautionDisplay label="Consignation électrique" prec={autorisation.prec_consignation_electrique} />
          <PrecautionDisplay label="Débranchement force motrice" prec={autorisation.prec_debranchement_force} />
          <PrecautionDisplay label="Vidange appareil/tuyauterie" prec={autorisation.prec_vidange_appareil} />
          <PrecautionDisplay label="Décontamination/lavage" prec={autorisation.prec_decontamination} />
          <PrecautionDisplay label="Dégazage" prec={autorisation.prec_degazage} />
          <PrecautionDisplay label="Pose joint plein" prec={autorisation.prec_pose_joint_plein} />
          <PrecautionDisplay label="Ventilation forcée" prec={autorisation.prec_ventilation_forcee} />
          <PrecautionDisplay label="Zone balisée" prec={autorisation.prec_zone_balisee} />
          <PrecautionDisplay label="Canalisations électriques" prec={autorisation.prec_canalisations_electriques} />
          <PrecautionDisplay label="Souterraines balisées" prec={autorisation.prec_souterraines_balisees} />
          <PrecautionDisplay label="Égouts et câbles" prec={autorisation.prec_egouts_cables} />
          <PrecautionDisplay label="Taux d'oxygène" prec={autorisation.prec_taux_oxygene} />
          <PrecautionDisplay label="Taux d'explosivité" prec={autorisation.prec_taux_explosivite} />
          <PrecautionDisplay label="Explosimètre continu" prec={autorisation.prec_explosimetre_continu} />
          <PrecautionDisplay label="Éclairage de sûreté" prec={autorisation.prec_eclairage_surete} />
          <PrecautionDisplay label="Extincteur type" prec={autorisation.prec_extincteur_type} />
          <PrecautionDisplay label="Autres (matérielles)" prec={autorisation.prec_autres_materielles} />
          <PrecautionDisplay label="Visière" prec={autorisation.prec_visiere} />
          <PrecautionDisplay label="Tenue imperméable" prec={autorisation.prec_tenue_impermeable} />
          <PrecautionDisplay label="Cagoule air" prec={autorisation.prec_cagoule_air} />
          <PrecautionDisplay label="Masque type" prec={autorisation.prec_masque_type} />
          <PrecautionDisplay label="Gant type" prec={autorisation.prec_gant_type} />
          <PrecautionDisplay label="Harnais sécurité" prec={autorisation.prec_harnais_securite} />
          <PrecautionDisplay label="Outillage anti-étincelle" prec={autorisation.prec_outillage_anti_etincelle} />
          <PrecautionDisplay label="Présence surveillant" prec={autorisation.prec_presence_surveillant} />
          <PrecautionDisplay label="Autres (EPI)" prec={autorisation.prec_autres_epi} />
        </CardContent>
      </Card>

      {/* Validation */}
      <Card>
        <CardHeader>
          <CardTitle>Validation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-sm font-semibold text-gray-600">Établie par</p>
            <p>{autorisation.etablie_par}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Délivrée à</p>
            <p>{autorisation.delivree_a}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Date de délivrance</p>
            <p>{autorisation.date_delivrance ? new Date(autorisation.date_delivrance).toLocaleDateString('fr-FR') : 'Non renseignée'}</p>
          </div>
          
          <div className="mt-6">
            <p className="text-sm font-semibold text-gray-600 mb-2">Vérifications post-intervention</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">30 minutes</p>
                <p className="font-mono">{autorisation.verif_30min_visa || '-'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">1 heure</p>
                <p className="font-mono">{autorisation.verif_1h_visa || '-'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">2 heures</p>
                <p className="font-mono">{autorisation.verif_2h_visa || '-'}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default AutorisationParticuliereView;
