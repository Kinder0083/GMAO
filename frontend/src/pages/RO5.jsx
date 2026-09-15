import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import {
  ChevronLeft, ChevronRight, Mic, MicOff, Send, Pencil, Trash2,
  Sparkles, Loader2, Keyboard, Check, X, NotebookPen
} from 'lucide-react';
import { ro5API } from '../services/api';
import { useToast } from '../hooks/use-toast';
import useAdriaVoice from '../components/Common/useAdriaVoice';
import RO5AnalyzeDialog from '../components/RO5/RO5AnalyzeDialog';

const MONTHS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];

const toDateKey = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

const RO5 = () => {
  const { toast } = useToast();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [analyzeOpen, setAnalyzeOpen] = useState(false);
  const inputRef = useRef(null);

  const currentMonth = currentDate.getMonth();
  const currentYear = currentDate.getFullYear();
  const selectedKey = toDateKey(selectedDate);
  const todayKey = toDateKey(new Date());

  const handleTranscription = async (text) => {
    setInput((prev) => (prev ? `${prev} ${text}` : text));
  };
  const voice = useAdriaVoice({ toast, onTranscription: handleTranscription });

  const loadMonth = useCallback(async () => {
    setLoading(true);
    try {
      const firstDay = new Date(currentYear, currentMonth, 1);
      const lastDay = new Date(currentYear, currentMonth + 1, 0);
      const res = await ro5API.list(toDateKey(firstDay), toDateKey(lastDay));
      setEntries(res.data || []);
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de charger le carnet de bord', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [currentMonth, currentYear, toast]);

  useEffect(() => { loadMonth(); }, [loadMonth]);

  const entriesByDate = useMemo(() => {
    const grouped = {};
    entries.forEach((e) => {
      if (!grouped[e.date]) grouped[e.date] = [];
      grouped[e.date].push(e);
    });
    return grouped;
  }, [entries]);

  const dayEntries = entriesByDate[selectedKey] || [];
  const pendingCount = dayEntries.filter((e) => e.status === 'pending').length;

  const getDaysInMonth = () => {
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDay = firstDay.getDay();
    const days = [];
    for (let i = 0; i < (startDay === 0 ? 6 : startDay - 1); i++) days.push(null);
    for (let day = 1; day <= daysInMonth; day++) days.push(day);
    return days;
  };
  const days = getDaysInMonth();

  const handleAdd = async () => {
    if (!input.trim() || saving) return;
    setSaving(true);
    try {
      const res = await ro5API.create({ content: input.trim(), date: selectedKey, source: 'text' });
      setEntries((prev) => [...prev, res.data]);
      setInput('');
    } catch (error) {
      toast({ title: 'Erreur', description: "Impossible d'ajouter l'entrée", variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  const handleVoiceStop = async () => {
    await voice.stopRecording();
  };

  const handleSaveEdit = async (id) => {
    if (!editValue.trim()) return;
    try {
      const res = await ro5API.update(id, editValue.trim());
      setEntries((prev) => prev.map((e) => (e.id === id ? res.data : e)));
      setEditingId(null);
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de corriger cette entrée', variant: 'destructive' });
    }
  };

  const handleDelete = async (id) => {
    try {
      await ro5API.delete(id);
      setEntries((prev) => prev.filter((e) => e.id !== id));
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de supprimer cette entrée', variant: 'destructive' });
    }
  };

  const handleAnalyzed = (processedEntryIds, links) => {
    // Met a jour localement les entrees traitees (statut + document lie) sans recharger le mois entier
    setEntries((prev) => prev.map((e) => {
      const link = links.find((l) => l.source_entry_ids?.includes(e.id));
      if (!link) return e;
      return { ...e, status: 'processed', linked_documents: [...(e.linked_documents || []), link.document] };
    }));
  };

  const formatTime = (iso) => {
    try { return new Date(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }); }
    catch { return ''; }
  };

  return (
    <div className="p-4 md:p-6 space-y-4 max-w-6xl mx-auto">
      <div className="flex items-center gap-2">
        <NotebookPen className="text-purple-600" />
        <h1 className="text-xl font-semibold">RO 5 / RO 30 / TT</h1>
      </div>
      <p className="text-sm text-gray-500">
        Notez rapidement une observation ou une demande, au clavier ou à la voix. Quand vous êtes prêt,
        demandez à Adria d'analyser la journée : elle proposera des demandes d'intervention à confirmer.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,360px)_1fr] gap-4">
        {/* Calendrier */}
        <Card>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-3">
              <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date(currentYear, currentMonth - 1, 1))}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="font-semibold">{MONTHS[currentMonth]} {currentYear}</h2>
              <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date(currentYear, currentMonth + 1, 1))}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid grid-cols-7 gap-1 mb-1">
              {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((d, i) => (
                <div key={i} className="text-center text-xs font-medium text-gray-400 py-1">{d}</div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, index) => {
                if (!day) return <div key={`empty-${index}`} className="h-10" />;
                const dateKey = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const dayList = entriesByDate[dateKey] || [];
                const hasPending = dayList.some((e) => e.status === 'pending');
                const isSelected = dateKey === selectedKey;
                const isToday = dateKey === todayKey;
                return (
                  <button
                    key={day}
                    type="button"
                    onClick={() => setSelectedDate(new Date(currentYear, currentMonth, day))}
                    className={`h-10 rounded-lg text-sm relative flex items-center justify-center transition-colors ${
                      isSelected ? 'bg-purple-600 text-white font-semibold'
                        : isToday ? 'bg-purple-50 text-purple-700 font-semibold border border-purple-300'
                        : 'hover:bg-gray-100'
                    }`}
                    data-testid={`ro5-day-${dateKey}`}
                  >
                    {day}
                    {hasPending && (
                      <span className={`absolute bottom-1 w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-white' : 'bg-orange-500'}`} />
                    )}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Journee selectionnee */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-base">
                {selectedDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
              </CardTitle>
              <Button
                onClick={() => setAnalyzeOpen(true)}
                disabled={pendingCount === 0}
                size="sm"
                className="bg-purple-600 hover:bg-purple-700 gap-1.5"
                data-testid="ro5-analyze-btn"
              >
                <Sparkles size={15} />
                Analyser cette journée {pendingCount > 0 && `(${pendingCount})`}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Composer */}
            <div className="flex gap-2">
              <Textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAdd(); } }}
                placeholder={voice.isRecording ? 'Enregistrement en cours…' : 'Notez une observation ou une demande…'}
                rows={2}
                disabled={voice.isRecording}
                className="flex-1 resize-none"
                data-testid="ro5-composer-input"
              />
              <div className="flex flex-col gap-2">
                <Button
                  variant={voice.isRecording ? 'destructive' : 'outline'}
                  size="icon"
                  onClick={voice.isRecording ? handleVoiceStop : voice.startRecording}
                  className={voice.isRecording ? 'animate-pulse' : ''}
                  data-testid="ro5-mic-btn"
                >
                  {voice.isRecording ? <MicOff size={16} /> : <Mic size={16} />}
                </Button>
                <Button size="icon" onClick={handleAdd} disabled={!input.trim() || saving} data-testid="ro5-send-btn">
                  {saving ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </Button>
              </div>
            </div>

            {/* Liste des entrees */}
            {loading ? (
              <div className="text-center py-8 text-sm text-gray-400">Chargement…</div>
            ) : dayEntries.length === 0 ? (
              <div className="text-center py-8 text-sm text-gray-400">Aucune entrée pour cette journée.</div>
            ) : (
              <div className="space-y-2">
                {dayEntries.map((entry) => (
                  <div key={entry.id} className="flex items-start gap-2 p-2.5 rounded-lg border border-gray-200 bg-gray-50" data-testid={`ro5-entry-${entry.id}`}>
                    <div className="mt-0.5 text-gray-400">
                      {entry.source === 'voice' ? <Mic size={14} /> : <Keyboard size={14} />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 text-xs text-gray-400 mb-0.5">
                        <span>{formatTime(entry.created_at)}</span>
                        {entry.status === 'processed' && entry.linked_documents?.map((doc, i) => (
                          <Badge key={i} variant="outline" className="text-[10px] gap-1 border-green-300 text-green-700">
                            <Check size={10} /> DI {doc.numero || ''}
                          </Badge>
                        ))}
                      </div>
                      {editingId === entry.id ? (
                        <div className="flex items-center gap-1.5">
                          <Textarea value={editValue} onChange={(e) => setEditValue(e.target.value)} rows={2} className="text-sm flex-1" />
                          <Button size="icon" variant="ghost" onClick={() => handleSaveEdit(entry.id)}><Check size={14} /></Button>
                          <Button size="icon" variant="ghost" onClick={() => setEditingId(null)}><X size={14} /></Button>
                        </div>
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{entry.content}</p>
                      )}
                    </div>
                    {editingId !== entry.id && (
                      <div className="flex items-center gap-0.5 flex-shrink-0">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => { setEditingId(entry.id); setEditValue(entry.content); }}>
                          <Pencil size={13} />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7 text-red-500" onClick={() => handleDelete(entry.id)}>
                          <Trash2 size={13} />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {analyzeOpen && (
        <RO5AnalyzeDialog
          open={analyzeOpen}
          date={selectedKey}
          onClose={() => setAnalyzeOpen(false)}
          onDone={handleAnalyzed}
        />
      )}
    </div>
  );
};

export default RO5;
