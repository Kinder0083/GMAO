import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Checkbox } from '../components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { ArrowLeft, Save, Printer } from 'lucide-react';
import { documentationsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { formatErrorMessage } from '../utils/errorFormatter';

function AutorisationParticuliereForm() {
  const { poleId, autorisationId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [pole, setPole] = useState(null);

  const [formData, setFormData] = useState({
    // Type de travaux
    type_point_chaud: false,
    type_espace_clos: false,
    type_fouille: false,
    type_autre: false,
    type_autre_precision: '',
    
    // Détails
    detail_travaux: '',
    
    // Lieu
    lieu_materiel_appareillage: '',
    lieu_dernier_produit: '',
    lieu_danger_avoisinant: '',
    
    // Précautions (26 lignes avec 3 états)
    prec_consignation_materiel: { non: false, oui: false, fait: false },
    prec_consignation_electrique: { non: false, oui: false, fait: false },
    prec_debranchement_force: { non: false, oui: false, fait: false },
    prec_vidange_appareil: { non: false, oui: false, fait: false },
    prec_decontamination: { non: false, oui: false, fait: false },
    prec_degazage: { non: false, oui: false, fait: false },
    prec_pose_joint_plein: { non: false, oui: false, fait: false },
    prec_ventilation_forcee: { non: false, oui: false, fait: false },
    prec_zone_balisee: { non: false, oui: false, fait: false },
    prec_canalisations_electriques: { non: false, oui: false, fait: false },
    prec_souterraines_balisees: { non: false, oui: false, fait: false },
    prec_egouts_cables: { non: false, oui: false, fait: false },
    prec_taux_oxygene: { non: false, oui: false, fait: false },
    prec_taux_explosivite: { non: false, oui: false, fait: false },
    prec_explosimetre_continu: { non: false, oui: false, fait: false },
    prec_eclairage_surete: { non: false, oui: false, fait: false },
    prec_extincteur_type: { non: false, oui: false, fait: false },
    prec_extincteur_type_precision: '',
    prec_autres_materielles: { non: false, oui: false, fait: false },
    prec_autres_materielles_precision: '',
    prec_visiere: { non: false, oui: false, fait: false },
    prec_tenue_impermeable: { non: false, oui: false, fait: false },
    prec_cagoule_air: { non: false, oui: false, fait: false },
    prec_masque_type: { non: false, oui: false, fait: false },
    prec_masque_type_precision: '',
    prec_gant_type: { non: false, oui: false, fait: false },
    prec_gant_type_precision: '',
    prec_harnais_securite: { non: false, oui: false, fait: false },
    prec_outillage_anti_etincelle: { non: false, oui: false, fait: false },
    prec_presence_surveillant: { non: false, oui: false, fait: false },
    prec_autres_epi: { non: false, oui: false, fait: false },
    prec_autres_epi_precision: '',
    
    // Validation
    etablie_par: '',
    delivree_a: '',
    date_delivrance: new Date().toISOString().split('T')[0],
    
    // Vérifications
    verif_30min_visa: '',
    verif_1h_visa: '',
    verif_2h_visa: ''
  });

  useEffect(() => {
    loadData();
  }, [poleId, autorisationId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const poleData = await documentationsAPI.getPole(poleId);
      setPole(poleData);

      if (autorisationId && autorisationId !== 'new') {
        const autoData = await documentationsAPI.getAutorisation(autorisationId);
        setFormData(autoData);
      }
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

  const handlePrecautionChange = (precName, state) => {
    setFormData({
      ...formData,
      [precName]: {
        non: state === 'non',
        oui: state === 'oui',
        fait: state === 'fait'
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const data = {
        ...formData,
        pole_id: poleId
      };

      if (autorisationId && autorisationId !== 'new') {
        await documentationsAPI.updateAutorisation(autorisationId, data);
        toast({ title: 'Succès', description: 'Autorisation mise à jour' });
      } else {
        await documentationsAPI.createAutorisation(data);
        toast({ title: 'Succès', description: 'Autorisation créée' });
      }
      navigate(`/documentations/${poleId}`);
    } catch (error) {
      toast({
        title: 'Erreur',
        description: formatErrorMessage(error, 'Erreur lors de l\'enregistrement'),
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const PrecautionRow = ({ label, precName, precisionField }) => (
    <div className="border-b pb-3 mb-3">
      <div className="flex items-center justify-between mb-2">
        <Label className="flex-1">{label}</Label>
        <RadioGroup
          value={
            formData[precName]?.oui ? 'oui' :
            formData[precName]?.fait ? 'fait' :
            formData[precName]?.non ? 'non' : ''
          }
          onValueChange={(val) => handlePrecautionChange(precName, val)}
          className="flex gap-4"
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="non" id={`${precName}-non`} />
            <Label htmlFor={`${precName}-non`}>NON</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="oui" id={`${precName}-oui`} />
            <Label htmlFor={`${precName}-oui`}>OUI</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="fait" id={`${precName}-fait`} />
            <Label htmlFor={`${precName}-fait`}>FAIT</Label>
          </div>
        </RadioGroup>
      </div>
      {precisionField && (
        <Input
          placeholder="Préciser..."
          value={formData[precisionField] || ''}
          onChange={(e) => setFormData({ ...formData, [precisionField]: e.target.value })}
          className="mt-2"
        />
      )}
    </div>
  );

  if (loading && !pole) {
    return <div className="flex justify-center items-center h-screen">Chargement...</div>;
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <Button variant="ghost" onClick={() => navigate(`/documentations/${poleId}`)} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour au pôle
        </Button>
        <h1 className="text-3xl font-bold">Autorisation Particulière de Travaux</h1>
        <p className="text-gray-500">{pole?.nom || 'Pôle de service'}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section 1: Type de travaux */}
        <Card>
          <CardHeader>
            <CardTitle>1. Type de travaux concernés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="type_point_chaud"
                checked={formData.type_point_chaud}
                onCheckedChange={(checked) => setFormData({ ...formData, type_point_chaud: checked })}
              />
              <label htmlFor="type_point_chaud">Par point chaud</label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="type_espace_clos"
                checked={formData.type_espace_clos}
                onCheckedChange={(checked) => setFormData({ ...formData, type_espace_clos: checked })}
              />
              <label htmlFor="type_espace_clos">En espace clos ou confiné</label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="type_fouille"
                checked={formData.type_fouille}
                onCheckedChange={(checked) => setFormData({ ...formData, type_fouille: checked })}
              />
              <label htmlFor="type_fouille">De fouille</label>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="type_autre"
                  checked={formData.type_autre}
                  onCheckedChange={(checked) => setFormData({ ...formData, type_autre: checked })}
                />
                <label htmlFor="type_autre">Autre cas</label>
              </div>
              {formData.type_autre && (
                <Input
                  placeholder="Préciser le type de travaux..."
                  value={formData.type_autre_precision}
                  onChange={(e) => setFormData({ ...formData, type_autre_precision: e.target.value })}
                />
              )}
            </div>

            <div className="mt-4">
              <Label>Détail des travaux à réaliser *</Label>
              <Textarea
                value={formData.detail_travaux}
                onChange={(e) => setFormData({ ...formData, detail_travaux: e.target.value })}
                rows={4}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Section 2: Lieu et dangers */}
        <Card>
          <CardHeader>
            <CardTitle>2. Lieu d'intervention et dangers</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Matériel ou appareillage utilisé</Label>
              <Input
                value={formData.lieu_materiel_appareillage}
                onChange={(e) => setFormData({ ...formData, lieu_materiel_appareillage: e.target.value })}
              />
            </div>
            <div>
              <Label>Dernier produit ou fluide contenu</Label>
              <Input
                value={formData.lieu_dernier_produit}
                onChange={(e) => setFormData({ ...formData, lieu_dernier_produit: e.target.value })}
              />
            </div>
            <div>
              <Label>Appareil, matériel ou activité avoisinantes présentant un danger</Label>
              <Input
                value={formData.lieu_danger_avoisinant}
                onChange={(e) => setFormData({ ...formData, lieu_danger_avoisinant: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Section 3: Précautions */}
        <Card>
          <CardHeader>
            <CardTitle>3. Précautions à prendre</CardTitle>
            <p className="text-sm text-gray-600">Pour chaque précaution, sélectionnez NON, OUI ou FAIT</p>
          </CardHeader>
          <CardContent className="space-y-2">
            <PrecautionRow label="Consignation matériel ou pièce en mouvement" precName="prec_consignation_materiel" />
            <PrecautionRow label="Consignation électrique" precName="prec_consignation_electrique" />
            <PrecautionRow label="Débranchement force motrice" precName="prec_debranchement_force" />
            <PrecautionRow label="Vidange appareil/tuyauterie" precName="prec_vidange_appareil" />
            <PrecautionRow label="Décontamination/lavage" precName="prec_decontamination" />
            <PrecautionRow label="Dégazage" precName="prec_degazage" />
            <PrecautionRow label="Pose joint plein" precName="prec_pose_joint_plein" />
            <PrecautionRow label="Ventilation forcée" precName="prec_ventilation_forcee" />
            <PrecautionRow label="Zone balisée" precName="prec_zone_balisee" />
            <PrecautionRow label="Canalisations électriques" precName="prec_canalisations_electriques" />
            <PrecautionRow label="Souterraines balisées" precName="prec_souterraines_balisees" />
            <PrecautionRow label="Égouts et câbles protégés" precName="prec_egouts_cables" />
            <PrecautionRow label="Taux d'oxygène" precName="prec_taux_oxygene" />
            <PrecautionRow label="Taux d'explosivité" precName="prec_taux_explosivite" />
            <PrecautionRow label="Explosimètre en continu" precName="prec_explosimetre_continu" />
            <PrecautionRow label="Éclairage de sûreté" precName="prec_eclairage_surete" />
            <PrecautionRow label="Extincteur type" precName="prec_extincteur_type" precisionField="prec_extincteur_type_precision" />
            <PrecautionRow label="Autres (matérielles)" precName="prec_autres_materielles" precisionField="prec_autres_materielles_precision" />
            <PrecautionRow label="Visière" precName="prec_visiere" />
            <PrecautionRow label="Tenue imperméable, bottes" precName="prec_tenue_impermeable" />
            <PrecautionRow label="Cagoule air respirable/ART" precName="prec_cagoule_air" />
            <PrecautionRow label="Masque type" precName="prec_masque_type" precisionField="prec_masque_type_precision" />
            <PrecautionRow label="Gant type" precName="prec_gant_type" precisionField="prec_gant_type_precision" />
            <PrecautionRow label="Harnais de sécurité" precName="prec_harnais_securite" />
            <PrecautionRow label="Outillage anti-étincelle" precName="prec_outillage_anti_etincelle" />
            <PrecautionRow label="Présence d'un surveillant" precName="prec_presence_surveillant" />
            <PrecautionRow label="Autres (EPI)" precName="prec_autres_epi" precisionField="prec_autres_epi_precision" />
          </CardContent>
        </Card>

        {/* Section 4: Validation */}
        <Card>
          <CardHeader>
            <CardTitle>4. Validation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Cette autorisation est établie par *</Label>
              <Input
                value={formData.etablie_par}
                onChange={(e) => setFormData({ ...formData, etablie_par: e.target.value })}
                placeholder="Nom et visa"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Est délivrée à *</Label>
                <Input
                  value={formData.delivree_a}
                  onChange={(e) => setFormData({ ...formData, delivree_a: e.target.value })}
                  placeholder="Entreprise"
                  required
                />
              </div>
              <div>
                <Label>Le (date) *</Label>
                <Input
                  type="date"
                  value={formData.date_delivrance}
                  onChange={(e) => setFormData({ ...formData, date_delivrance: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="mt-6">
              <Label className="text-base font-semibold">Vérification post-intervention (Visas AM)</Label>
              <div className="grid grid-cols-3 gap-4 mt-3">
                <div>
                  <Label>30 minutes</Label>
                  <Input
                    value={formData.verif_30min_visa}
                    onChange={(e) => setFormData({ ...formData, verif_30min_visa: e.target.value })}
                    placeholder="Visa"
                  />
                </div>
                <div>
                  <Label>1 heure</Label>
                  <Input
                    value={formData.verif_1h_visa}
                    onChange={(e) => setFormData({ ...formData, verif_1h_visa: e.target.value })}
                    placeholder="Visa"
                  />
                </div>
                <div>
                  <Label>2 heures</Label>
                  <Input
                    value={formData.verif_2h_visa}
                    onChange={(e) => setFormData({ ...formData, verif_2h_visa: e.target.value })}
                    placeholder="Visa"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => navigate(`/documentations/${poleId}`)}>
            Annuler
          </Button>
          <Button type="submit" disabled={loading}>
            <Save className="mr-2 h-4 w-4" />
            {loading ? 'Enregistrement...' : 'Enregistrer'}
          </Button>
        </div>
      </form>
    </div>
  );
}

export default AutorisationParticuliereForm;
