import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, Download, Printer, Edit } from 'lucide-react';
import { documentationsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { formatErrorMessage } from '../utils/errorFormatter';

function BonDeTravailView() {
  const { poleId, bonId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [bon, setBon] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setCurrentUser(JSON.parse(userData));
    }
    loadBon();
  }, [bonId]);

  const loadBon = async () => {
    try {
      setLoading(true);
      const data = await documentationsAPI.getBonTravail(bonId);
      setBon(data);
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
    if (!currentUser || !bon) return false;
    if (currentUser.role === 'ADMIN') return true;
    return bon.created_by === currentUser.id;
  };

  const handlePrint = () => {
    const token = localStorage.getItem('token');
    // Note: L'URL du backend doit être configurée pour utiliser le prompt HTML/CSS que nous avons défini
    const printUrl = `${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/documentations/bons-travail/${bonId}/pdf?token=${token}`;
    const printWindow = window.open(printUrl, '_blank');
    if (printWindow) {
      // Tenter de lancer l'impression sur la nouvelle fenêtre
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print();
        }, 1000); // Un délai peut être nécessaire pour que le PDF charge
      };
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Chargement...</div>;
  }

  if (!bon) {
    return <div className="text-center text-gray-500 py-12">Bon de travail non trouvé</div>;
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/documentations/${poleId}`)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{bon.titre || "Bon de travail"}</h1>
            <p className="text-gray-500">
              Créé le {bon.created_at ? new Date(bon.created_at).toLocaleDateString('fr-FR') : 'Date inconnue'}
            </p>
            {bon.entreprise && (
              <Badge variant="outline" className="mt-2">
                {bon.entreprise}
              </Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {canEdit() && (
            <Button
              variant="outline"
              onClick={() => navigate(`/documentations/${poleId}/bon-de-travail/${bonId}/edit`)}
            >
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
              window.open(`${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/documentations/bons-travail/${bonId}/pdf?token=${token}`, '_blank');
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            Télécharger PDF
          </Button>
        </div>
      </div>
      
      {/* Introduction (Statique du DOCX) */}
      <Card className="bg-gray-50 border-gray-300">
        <CardContent className="pt-6 italic text-sm text-gray-700">
          <p>Le bon de travail, permet d’identifier les risques liés aux travaux spécifiés ci-dessous ainsi que les précautions à prendre pour éviter tout accident, dégât matériel ou atteinte à l’environnement. Ce bon de travail tient lieu de plan de prévention. Sauf contre-indication particulière (ou modification des conditions d’intervention), le bon de travail est valable pour toute la durée du chantier (dans la limite de 24 heures).</p>
        </CardContent>
      </Card>

      {/* Travaux à réaliser */}
      <Card>
        <CardHeader>
          <CardTitle>1. Travaux à réaliser</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-semibold text-gray-600">Localisation / Ligne</p>
            <p className="text-base">{bon.localisation_ligne || 'Non renseigné'}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Description des travaux</p>
            <p className="text-base whitespace-pre-wrap">{bon.description_travaux || 'Non renseigné'}</p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600">Nom des intervenants</p>
            <p className="text-base">{bon.nom_intervenants || 'Non renseigné'}</p>
          </div>
        </CardContent>
      </Card>

      {/* Risques identifiés */}
      <Card>
        <CardHeader>
          <CardTitle>2. Risques identifiés</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Intervention sur du matériel ou des infrastructures</p>
            <div className="flex flex-wrap gap-2">
              {bon.risques_materiel?.length > 0 ? (
                bon.risques_materiel.map((r, i) => (
                  <Badge key={i} variant="secondary">{r}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucun</span>
              )}
            </div>
            {bon.risques_materiel_autre && (
              <p className="text-sm mt-2 text-gray-600">Autre: {bon.risques_materiel_autre}</p>
            )}
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Travaux nécessitant une autorisation particulière</p>
            <div className="flex flex-wrap gap-2">
              {bon.risques_autorisation?.length > 0 ? (
                bon.risques_autorisation.map((r, i) => (
                  <Badge key={i} variant="secondary">{r}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucun</span>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Produits dangereux</p>
            <div className="flex flex-wrap gap-2">
              {bon.risques_produits?.length > 0 ? (
                bon.risques_produits.map((r, i) => (
                  <Badge key={i} variant="secondary">{r}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucun</span>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Environnement des travaux nécessitant une attention particulière</p>
            <div className="flex flex-wrap gap-2">
              {bon.risques_environnement?.length > 0 ? (
                bon.risques_environnement.map((r, i) => (
                  <Badge key={i} variant="secondary">{r}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucun</span>
              )}
            </div>
            {bon.risques_environnement_autre && (
              <p className="text-sm mt-2 text-gray-600">Autre: {bon.risques_environnement_autre}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Précautions à prendre */}
      <Card>
        <CardHeader>
          <CardTitle>3. Précautions à prendre</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Sur le matériel ou les infrastructures</p>
            <div className="flex flex-wrap gap-2">
              {bon.precautions_materiel?.length > 0 ? (
                bon.precautions_materiel.map((p, i) => (
                  <Badge key={i} variant="outline">{p}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucune</span>
              )}
            </div>
            {bon.precautions_materiel_autre && (
              <p className="text-sm mt-2 text-gray-600">Autre: {bon.precautions_materiel_autre}</p>
            )}
            <p className="text-xs italic text-gray-600 mt-2">
              L’utilisation d’un chariot ou d’une nacelle n’est possible qu’après que l’entreprise intervenante ait fourni à IRIS une autorisation nominative de conduite.
            </p>
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Sur les hommes, le matériel ou l’environnement (EPI)</p>
            <div className="flex flex-wrap gap-2">
              {bon.precautions_epi?.length > 0 ? (
                bon.precautions_epi.map((p, i) => (
                  <Badge key={i} variant="outline">{p}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucun</span>
              )}
            </div>
            {bon.precautions_epi_autre && (
              <p className="text-sm mt-2 text-gray-600">Autre: {bon.precautions_epi_autre}</p>
            )}
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Sur l’environnement des travaux</p>
            <div className="flex flex-wrap gap-2">
              {bon.precautions_environnement?.length > 0 ? (
                bon.precautions_environnement.map((p, i) => (
                  <Badge key={i} variant="outline">{p}</Badge>
                ))
              ) : (
                <span className="text-gray-400 text-sm">Aucune</span>
              )}
            </div>
            {bon.precautions_environnement_autre && (
              <p className="text-sm mt-2 text-gray-600">Autre: {bon.precautions_environnement_autre}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Engagement */}
      <Card>
        <CardHeader>
          <CardTitle>4. Engagement</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-700">
            Le représentant de l’entreprise intervenante reconnaît avoir pris connaissance des risques liés aux travaux qui lui sont confiés et s’engage à appliquer et faire appliquer les mesures de précaution qui lui ont été notifiées.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border-t pt-4">
            <div>
              <p className="text-sm font-semibold text-gray-600">Date d'engagement</p>
              <p className="text-base">
                {bon.date_engagement ? new Date(bon.date_engagement).toLocaleDateString('fr-FR') : 'Non renseignée'}
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-600">Nom Agent de Maîtrise (demandeur)</p>
              <p className="text-base">{bon.nom_agent_maitrise || 'Non renseigné'}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-600">Nom Représentant (intervenant)</p>
              <p className="text-base">{bon.nom_representant || 'Non renseigné'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Footer (Statique du DOCX) */}
      <div className="text-center text-xs text-gray-500 py-4">
        Remettre une copie à l’intervenant – Archivage Direction du site
      </div>
    </div>
  );
}

export default BonDeTravailView;
