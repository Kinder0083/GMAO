import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/select';
import { Loader2, Sparkles, Check, AlertCircle, Wrench } from 'lucide-react';
import { ro5API, equipmentsAPI, interventionRequestsAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';

const PRIORITES = ['URGENTE', 'HAUTE', 'MOYENNE', 'NORMALE', 'BASSE'];

function matchEquipment(equipmentList, nom) {
  if (!nom) return null;
  const search = nom.toLowerCase();
  return equipmentList.find((eq) =>
    eq.nom?.toLowerCase().includes(search) || eq.reference?.toLowerCase().includes(search)
  ) || null;
}

function RO5AnalyzeDialog({ open, date, onClose, onDone }) {
  const { toast } = useToast();
  const [step, setStep] = useState('analyzing'); // analyzing | review | done
  const [proposals, setProposals] = useState([]);
  const [equipmentList, setEquipmentList] = useState([]);
  const [links, setLinks] = useState([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [eqRes, analyzeRes] = await Promise.all([
          equipmentsAPI.getAll(),
          ro5API.analyze(date),
        ]);
        if (cancelled) return;
        const eqList = eqRes.data || [];
        setEquipmentList(eqList);
        const withState = (analyzeRes.data?.proposals || []).map((p, i) => {
          const match = matchEquipment(eqList, p.equipement_nom);
          return {
            ...p,
            _key: i,
            _status: 'idle', // idle | creating | done | error
            equipement_nom: match?.nom || p.equipement_nom || '',
            equipement_id: match?.id || null,
          };
        });
        setProposals(withState);
        setStep('review');
      } catch (error) {
        if (cancelled) return;
        toast({ title: 'Erreur', description: error.response?.data?.detail || "Échec de l'analyse IA", variant: 'destructive' });
        onClose();
      }
    })();
    return () => { cancelled = true; };
  }, [date]);

  const updateProposal = (key, patch) => {
    setProposals((prev) => prev.map((p) => (p._key === key ? { ...p, ...patch } : p)));
  };

  const handleEquipmentBlur = (key, value) => {
    const match = matchEquipment(equipmentList, value);
    updateProposal(key, { equipement_nom: value, equipement_id: match?.id || null });
  };

  const handleCreate = async (proposal) => {
    updateProposal(proposal._key, { _status: 'creating' });
    try {
      const payload = {
        titre: proposal.titre,
        description: proposal.description,
        priorite: proposal.priorite,
        equipement_id: proposal.equipement_id || null,
        date_limite_desiree: proposal.date_limite ? new Date(proposal.date_limite).toISOString() : null,
      };
      const res = await interventionRequestsAPI.create(payload);
      const created = res.data;

      const linkDoc = { type: 'intervention_request', id: created.id, numero: created.numero || created.id?.slice(-4), titre: created.titre };
      await Promise.all(
        (proposal.source_entry_ids || []).map((entryId) => ro5API.link(entryId, linkDoc))
      );

      updateProposal(proposal._key, { _status: 'done' });
      setLinks((prev) => [...prev, { source_entry_ids: proposal.source_entry_ids, document: linkDoc }]);
      toast({ title: 'Demande créée', description: `DI "${created.titre}" créée avec succès` });
    } catch (error) {
      updateProposal(proposal._key, { _status: 'error' });
      toast({ title: 'Erreur', description: error.response?.data?.detail || 'Échec de la création', variant: 'destructive' });
    }
  };

  const handleClose = () => {
    onDone(proposals.filter((p) => p._status === 'done').flatMap((p) => p.source_entry_ids), links);
    onClose();
  };

  const allDone = proposals.length > 0 && proposals.every((p) => p._status === 'done');

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col" data-testid="ro5-analyze-dialog">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            {step === 'analyzing' && 'Adria analyse la journée…'}
            {step === 'review' && 'Propositions de demandes d\'intervention'}
          </DialogTitle>
        </DialogHeader>

        {step === 'analyzing' && (
          <div className="flex flex-col items-center justify-center py-12 space-y-3">
            <Loader2 className="h-9 w-9 animate-spin text-purple-600" />
            <p className="text-sm text-gray-500">Lecture des notes de la journée…</p>
          </div>
        )}

        {step === 'review' && proposals.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 space-y-2 text-center">
            <AlertCircle className="h-8 w-8 text-gray-300" />
            <p className="text-sm text-gray-500">Aucune action détectée dans les notes de cette journée.</p>
          </div>
        )}

        {step === 'review' && proposals.length > 0 && (
          <ScrollArea className="h-[55vh] pr-2">
            <div className="space-y-3">
              {proposals.map((p) => (
                <div
                  key={p._key}
                  className={`border rounded-lg p-3 space-y-2.5 ${p._status === 'done' ? 'border-green-300 bg-green-50/50' : 'border-gray-200'}`}
                  data-testid={`ro5-proposal-${p._key}`}
                >
                  <p className="text-sm text-purple-700 italic">« {p.resume} »</p>

                  <div className="space-y-1">
                    <Label className="text-xs">Titre</Label>
                    <Input
                      value={p.titre}
                      onChange={(e) => updateProposal(p._key, { titre: e.target.value })}
                      disabled={p._status === 'done'}
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">Description</Label>
                    <Textarea
                      value={p.description}
                      onChange={(e) => updateProposal(p._key, { description: e.target.value })}
                      rows={2}
                      disabled={p._status === 'done'}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label className="text-xs flex items-center gap-1"><Wrench size={11} /> Équipement</Label>
                      <Input
                        value={p.equipement_nom}
                        onChange={(e) => updateProposal(p._key, { equipement_nom: e.target.value })}
                        onBlur={(e) => handleEquipmentBlur(p._key, e.target.value)}
                        placeholder="Nom de l'équipement"
                        disabled={p._status === 'done'}
                      />
                      {p.equipement_nom && (
                        <span className={`text-[11px] ${p.equipement_id ? 'text-green-600' : 'text-amber-600'}`}>
                          {p.equipement_id ? 'Équipement reconnu' : 'Non trouvé — la DI sera créée sans équipement lié'}
                        </span>
                      )}
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Priorité</Label>
                      <Select value={p.priorite} onValueChange={(v) => updateProposal(p._key, { priorite: v })} disabled={p._status === 'done'}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {PRIORITES.map((pr) => <SelectItem key={pr} value={pr}>{pr}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs">Échéance désirée</Label>
                    <Input
                      type="date"
                      value={p.date_limite || ''}
                      onChange={(e) => updateProposal(p._key, { date_limite: e.target.value })}
                      disabled={p._status === 'done'}
                    />
                  </div>

                  <div className="flex justify-end">
                    {p._status === 'done' ? (
                      <Badge className="bg-green-600 gap-1"><Check size={12} /> DI créée</Badge>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => handleCreate(p)}
                        disabled={p._status === 'creating' || !p.titre.trim()}
                        className="bg-purple-600 hover:bg-purple-700"
                        data-testid={`ro5-create-di-${p._key}`}
                      >
                        {p._status === 'creating' ? <Loader2 size={14} className="animate-spin mr-1.5" /> : null}
                        Créer la demande d'intervention
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}

        {step === 'review' && (
          <div className="flex justify-end pt-2 border-t">
            <Button variant="outline" onClick={handleClose}>{allDone ? 'Terminer' : 'Fermer'}</Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default RO5AnalyzeDialog;
