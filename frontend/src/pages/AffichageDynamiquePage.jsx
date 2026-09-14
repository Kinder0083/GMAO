import React, { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { BACKEND_URL } from '../utils/config';
import { useToast } from '../hooks/use-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '../components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../components/ui/dialog';
import {
  Tv, Plus, Save, Link as LinkIcon, Trash2, RefreshCw, X, Copy, Undo2,
  Settings2, Maximize2, LayoutTemplate, Sun, Moon,
} from 'lucide-react';
import BlockContent, { BLOCK_TYPES, KPI_METRICS, THEMES, isBlockInAlert } from '../components/AffichageDynamique/BlockRenderer';

const API = BACKEND_URL;
const getHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('token')}` });

const DESIGN_W = 1920;
const DESIGN_H = 1080;
const MIN_W = 160;
const MIN_H = 100;
const PREVIEW_POLL_MS = 10000;
const GRID = 10;
const MAX_HISTORY = 30;
const snapGrid = (v) => Math.round(v / GRID) * GRID;

function newBlockId() {
  return (crypto.randomUUID ? crypto.randomUUID() : `blk-${Date.now()}-${Math.random().toString(36).slice(2)}`);
}

export default function AffichageDynamiquePage() {
  const { toast } = useToast();
  const [screens, setScreens] = useState([]);
  const [screenId, setScreenId] = useState(null);
  const [screen, setScreen] = useState(null); // { id, nom, blocks, is_active }
  const [selectedId, setSelectedId] = useState(null);
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const [machines, setMachines] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [equipments, setEquipments] = useState([]);

  const [showNewDialog, setShowNewDialog] = useState(false);
  const [newName, setNewName] = useState('');
  const [templates, setTemplates] = useState([]);
  const [newTemplate, setNewTemplate] = useState('');

  const [showLinkDialog, setShowLinkDialog] = useState(false);
  const [publicToken, setPublicToken] = useState(null);

  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const [showFullscreenPreview, setShowFullscreenPreview] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);

  const [scale, setScale] = useState(0.5);
  const wrapperRef = useRef(null);
  const dragRef = useRef(null);
  const draggingRef = useRef(false);
  const historyRef = useRef([]); // pile d'états précédents de `blocks` pour Annuler (Ctrl+Z)

  // ===== Chargement initial =====
  useEffect(() => {
    (async () => {
      try {
        const [screensRes, machinesRes, sensorsRes, equipmentsRes, templatesRes] = await Promise.all([
          axios.get(`${API}/api/affichage-dynamique`, { headers: getHeaders() }),
          axios.get(`${API}/api/affichage-dynamique/sources/machines`, { headers: getHeaders() }),
          axios.get(`${API}/api/affichage-dynamique/sources/sensors`, { headers: getHeaders() }),
          axios.get(`${API}/api/affichage-dynamique/sources/equipments`, { headers: getHeaders() }),
          axios.get(`${API}/api/affichage-dynamique/templates`, { headers: getHeaders() }).catch(() => ({ data: [] })),
        ]);
        setScreens(screensRes.data);
        setMachines(machinesRes.data);
        setSensors(sensorsRes.data);
        setEquipments(equipmentsRes.data);
        setTemplates(templatesRes.data);
        if (screensRes.data.length > 0) {
          setScreenId(screensRes.data[0].id);
        } else {
          setLoading(false);
        }
      } catch (e) {
        toast({ title: 'Erreur', description: "Impossible de charger l'Affichage Dynamique.", variant: 'destructive' });
        setLoading(false);
      }
    })();
  }, []);

  // ===== Chargement de l'écran sélectionné =====
  useEffect(() => {
    if (!screenId) return;
    setLoading(true);
    setSelectedId(null);
    historyRef.current = [];
    axios.get(`${API}/api/affichage-dynamique/${screenId}`, { headers: getHeaders() })
      .then(({ data }) => {
        setScreen({ theme: 'dark', header: { enabled: false, title: '', logo_url: '' }, ...data });
        setDirty(false);
      })
      .catch(() => toast({ title: 'Erreur', description: "Impossible de charger l'écran.", variant: 'destructive' }))
      .finally(() => setLoading(false));
  }, [screenId]);

  // ===== Prévisualisation avec données réelles (polling) =====
  useEffect(() => {
    if (!screenId) return;
    const poll = async () => {
      if (draggingRef.current) return;
      try {
        const { data } = await axios.get(`${API}/api/affichage-dynamique/${screenId}/preview`, { headers: getHeaders() });
        setScreen((prev) => {
          if (!prev) return prev;
          const dataById = Object.fromEntries((data.blocks || []).map((b) => [b.id, b.data]));
          return { ...prev, blocks: prev.blocks.map((b) => ({ ...b, data: dataById[b.id] ?? b.data })) };
        });
        setLastRefresh(new Date());
      } catch (e) {
        // silencieux : la prévisualisation n'est pas critique
      }
    };
    poll();
    const id = setInterval(poll, PREVIEW_POLL_MS);
    return () => clearInterval(id);
  }, [screenId]);

  // ===== Mise à l'échelle du canvas =====
  useEffect(() => {
    const updateScale = () => {
      if (!wrapperRef.current) return;
      const availableW = wrapperRef.current.clientWidth - 32;
      setScale(Math.max(0.15, Math.min(1, availableW / DESIGN_W)));
    };
    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, []);

  const selectedBlock = screen?.blocks?.find((b) => b.id === selectedId) || null;

  const pushHistory = useCallback((blocksSnapshot) => {
    historyRef.current = [...historyRef.current.slice(-(MAX_HISTORY - 1)), blocksSnapshot];
  }, []);

  const mutateBlocks = useCallback((updater) => {
    setScreen((prev) => {
      if (!prev) return prev;
      pushHistory(prev.blocks);
      return { ...prev, blocks: updater(prev.blocks) };
    });
    setDirty(true);
  }, [pushHistory]);

  const undo = useCallback(() => {
    const prevBlocks = historyRef.current.pop();
    if (prevBlocks === undefined) return;
    setScreen((prev) => (prev ? { ...prev, blocks: prevBlocks } : prev));
    setDirty(true);
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        const tag = document.activeElement?.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA') return;
        e.preventDefault();
        undo();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [undo]);

  const addBlock = (type) => {
    const def = BLOCK_TYPES.find((t) => t.type === type);
    if (!def || !screen) return;
    const count = screen.blocks.length;
    const block = {
      id: newBlockId(),
      type,
      x: 60 + (count % 5) * 40,
      y: 60 + (count % 5) * 30,
      w: def.defaultW,
      h: def.defaultH,
      config: { ...def.defaultConfig },
    };
    mutateBlocks((blocks) => [...blocks, block]);
    setSelectedId(block.id);
  };

  const updateConfig = (id, patch) => {
    mutateBlocks((blocks) => blocks.map((b) => (b.id === id ? { ...b, config: { ...b.config, ...patch } } : b)));
  };

  const deleteBlock = (id) => {
    mutateBlocks((blocks) => blocks.filter((b) => b.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  // ===== Drag & resize (souris) =====
  const onBlockMouseDown = (e, block, mode) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedId(block.id);
    draggingRef.current = true;
    if (screen) pushHistory(screen.blocks);
    dragRef.current = {
      mode,
      startX: e.clientX,
      startY: e.clientY,
      origX: block.x,
      origY: block.y,
      origW: block.w,
      origH: block.h,
      id: block.id,
    };
    window.addEventListener('mousemove', onWindowMouseMove);
    window.addEventListener('mouseup', onWindowMouseUp);
  };

  const onWindowMouseMove = (e) => {
    const d = dragRef.current;
    if (!d) return;
    const dx = (e.clientX - d.startX) / scale;
    const dy = (e.clientY - d.startY) / scale;
    if (d.mode === 'drag') {
      const x = snapGrid(Math.max(0, d.origX + dx));
      const y = snapGrid(Math.max(0, d.origY + dy));
      mutateBlocksRaw((blocks) => blocks.map((b) => (b.id === d.id ? { ...b, x, y } : b)));
    } else {
      const w = snapGrid(Math.max(MIN_W, d.origW + dx));
      const h = snapGrid(Math.max(MIN_H, d.origH + dy));
      mutateBlocksRaw((blocks) => blocks.map((b) => (b.id === d.id ? { ...b, w, h } : b)));
    }
  };

  // Pendant le drag, on met à jour la position sans re-render lourd via setScreen direct
  const mutateBlocksRaw = (updater) => {
    setScreen((prev) => (prev ? { ...prev, blocks: updater(prev.blocks) } : prev));
  };

  const onWindowMouseUp = () => {
    draggingRef.current = false;
    dragRef.current = null;
    setDirty(true);
    window.removeEventListener('mousemove', onWindowMouseMove);
    window.removeEventListener('mouseup', onWindowMouseUp);
  };

  useEffect(() => () => {
    window.removeEventListener('mousemove', onWindowMouseMove);
    window.removeEventListener('mouseup', onWindowMouseUp);
  }, []);

  // ===== Sauvegarde =====
  const save = async () => {
    if (!screen) return;
    setSaving(true);
    try {
      const blocks = screen.blocks.map(({ data, ...rest }) => rest);
      const payload = { blocks, theme: screen.theme || 'dark', header: screen.header || { enabled: false } };
      const { data } = await axios.put(`${API}/api/affichage-dynamique/${screen.id}`, payload, { headers: getHeaders() });
      setScreen((prev) => ({ ...prev, blocks: data.blocks, theme: data.theme, header: data.header }));
      setDirty(false);
      toast({ title: 'Enregistré', description: "L'écran a été mis à jour." });
    } catch (e) {
      toast({ title: 'Erreur', description: "L'enregistrement a échoué.", variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  // ===== Nouvel écran =====
  const createScreen = async () => {
    if (!newName.trim()) return;
    try {
      const { data } = await axios.post(`${API}/api/affichage-dynamique`, { nom: newName.trim(), blocks: [], template: newTemplate || null }, { headers: getHeaders() });
      setScreens((prev) => [data, ...prev]);
      setScreenId(data.id);
      setShowNewDialog(false);
      setNewName('');
      setNewTemplate('');
    } catch (e) {
      toast({ title: 'Erreur', description: "Création de l'écran impossible.", variant: 'destructive' });
    }
  };

  const deleteScreen = async () => {
    if (!screen) return;
    if (!window.confirm(`Supprimer l'écran "${screen.nom}" ? Cette action est irréversible.`)) return;
    try {
      await axios.delete(`${API}/api/affichage-dynamique/${screen.id}`, { headers: getHeaders() });
      const remaining = screens.filter((s) => s.id !== screen.id);
      setScreens(remaining);
      setScreen(null);
      setScreenId(remaining[0]?.id || null);
      toast({ title: 'Écran supprimé' });
    } catch (e) {
      toast({ title: 'Erreur', description: 'Suppression impossible.', variant: 'destructive' });
    }
  };

  // ===== Lien public =====
  const openLinkDialog = async () => {
    if (!screen) return;
    try {
      const { data } = await axios.get(`${API}/api/affichage-dynamique/${screen.id}/public-link`, { headers: getHeaders() });
      setPublicToken(data.public_token);
      setShowLinkDialog(true);
    } catch (e) {
      toast({ title: 'Erreur', description: 'Impossible de récupérer le lien public.', variant: 'destructive' });
    }
  };

  const regenerateToken = async () => {
    if (!screen) return;
    if (!window.confirm("Régénérer le lien invalidera l'ancien lien public (le lecteur de signalétique devra être reconfiguré). Continuer ?")) return;
    try {
      const { data } = await axios.post(`${API}/api/affichage-dynamique/${screen.id}/regenerate-token`, {}, { headers: getHeaders() });
      setPublicToken(data.public_token);
      toast({ title: 'Lien régénéré', description: "Pensez à mettre à jour le lecteur de signalétique." });
    } catch (e) {
      toast({ title: 'Erreur', description: 'Régénération impossible.', variant: 'destructive' });
    }
  };

  const publicUrl = publicToken ? `${window.location.origin}/affichage-public/${publicToken}` : '';

  const copyLink = () => {
    navigator.clipboard.writeText(publicUrl);
    toast({ title: 'Lien copié' });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Barre d'outils */}
      <div className="flex items-center justify-between gap-3 px-6 py-3 border-b bg-white">
        <div className="flex items-center gap-3">
          <Tv className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-gray-800">Affichage Dynamique</span>
          {screens.length > 0 && (
            <Select value={screenId || ''} onValueChange={setScreenId}>
              <SelectTrigger className="w-56"><SelectValue placeholder="Écran" /></SelectTrigger>
              <SelectContent>
                {screens.map((s) => (
                  <SelectItem key={s.id} value={s.id}>{s.nom}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <Button variant="outline" size="sm" onClick={() => setShowNewDialog(true)}>
            <Plus className="h-4 w-4 mr-1" /> Nouvel écran
          </Button>
        </div>
        {screen && (
          <div className="flex items-center gap-2">
            {lastRefresh && (
              <span className="hidden md:flex items-center gap-1.5 text-xs text-gray-400 mr-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 ad-live-dot" />
                Données à {lastRefresh.toLocaleTimeString('fr-FR')}
              </span>
            )}
            <Button variant="outline" size="sm" onClick={undo} title="Annuler (Ctrl+Z)">
              <Undo2 className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowFullscreenPreview(true)}>
              <Maximize2 className="h-4 w-4 mr-1" /> Aperçu
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowSettingsDialog(true)}>
              <Settings2 className="h-4 w-4 mr-1" /> Réglages
            </Button>
            <Button variant="outline" size="sm" onClick={openLinkDialog}>
              <LinkIcon className="h-4 w-4 mr-1" /> Lien public
            </Button>
            <Button variant="outline" size="sm" onClick={deleteScreen}>
              <Trash2 className="h-4 w-4 mr-1" /> Supprimer
            </Button>
            <Button size="sm" onClick={save} disabled={!dirty || saving}>
              <Save className="h-4 w-4 mr-1" /> {saving ? 'Enregistrement…' : 'Enregistrer'}
            </Button>
          </div>
        )}
      </div>

      {!loading && screens.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-3">
          <Tv className="h-10 w-10 text-gray-300" />
          <p>Aucun écran pour le moment.</p>
          <Button onClick={() => setShowNewDialog(true)}><Plus className="h-4 w-4 mr-1" /> Créer un écran</Button>
        </div>
      )}

      {screen && (
        <div className="flex flex-1 overflow-hidden">
          {/* Palette de blocs */}
          <div className="w-56 border-r bg-gray-50 p-3 overflow-y-auto shrink-0">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Blocs</div>
            <div className="flex flex-col gap-2">
              {BLOCK_TYPES.map((bt) => (
                <button
                  key={bt.type}
                  onClick={() => addBlock(bt.type)}
                  className="flex items-center gap-2 text-sm text-left px-3 py-2 rounded-lg border bg-white hover:border-blue-300 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: bt.accent }} />
                  <bt.icon className="h-4 w-4 shrink-0" style={{ color: bt.accent }} />
                  {bt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Canvas */}
          <div ref={wrapperRef} className="flex-1 overflow-auto p-4 bg-[radial-gradient(circle,_#e5e7eb_1px,_transparent_1px)] bg-[length:20px_20px]">
            <div style={{ width: DESIGN_W * scale, height: DESIGN_H * scale }}>
              <div
                style={{ width: DESIGN_W, height: DESIGN_H, transform: `scale(${scale})`, transformOrigin: 'top left', position: 'relative', background: THEMES[screen.theme || 'dark'].pageBg, borderRadius: 8 }}
                onMouseDown={() => setSelectedId(null)}
              >
                {screen.blocks.map((block) => {
                  const t = THEMES[screen.theme || 'dark'];
                  return (
                  <div
                    key={block.id}
                    onMouseDown={(e) => onBlockMouseDown(e, block, 'drag')}
                    className={isBlockInAlert(block) ? 'ad-alert-border' : ''}
                    style={{
                      position: 'absolute',
                      left: block.x,
                      top: block.y,
                      width: block.w,
                      height: block.h,
                      background: t.tileBg,
                      border: selectedId === block.id ? '2px solid #2563eb' : `1px solid ${t.tileBorder}`,
                      borderRadius: 20,
                      overflow: 'hidden',
                      cursor: 'move',
                    }}
                  >
                    <BlockContent block={block} theme={screen.theme || 'dark'} />
                    {selectedId === block.id && (
                      <>
                        <button
                          onMouseDown={(e) => { e.stopPropagation(); deleteBlock(block.id); }}
                          style={{ position: 'absolute', top: 8, right: 8, background: '#f87171', borderRadius: 999, width: 24, height: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: 'pointer' }}
                        >
                          <X size={14} color="#fff" />
                        </button>
                        <div
                          onMouseDown={(e) => onBlockMouseDown(e, block, 'resize')}
                          style={{ position: 'absolute', bottom: 0, right: 0, width: 18, height: 18, cursor: 'nwse-resize', background: '#2563eb', borderTopLeftRadius: 6 }}
                        />
                      </>
                    )}
                  </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Inspecteur */}
          <div className="w-72 border-l bg-white p-4 overflow-y-auto shrink-0">
            {selectedBlock ? (
              <BlockInspector
                block={selectedBlock}
                machines={machines}
                sensors={sensors}
                equipments={equipments}
                onChange={(patch) => updateConfig(selectedBlock.id, patch)}
              />
            ) : (
              <div className="text-sm text-gray-400">Sélectionnez un bloc pour le configurer.</div>
            )}
          </div>
        </div>
      )}

      {/* Dialog nouvel écran */}
      <Dialog open={showNewDialog} onOpenChange={setShowNewDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nouvel écran</DialogTitle></DialogHeader>
          <div className="space-y-2">
            <Label>Nom de l'écran</Label>
            <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Ex: Atelier Production" onKeyDown={(e) => e.key === 'Enter' && createScreen()} />
          </div>
          <div className="space-y-2">
            <Label>Modèle de départ (optionnel)</Label>
            <div className="grid grid-cols-1 gap-2">
              <button
                type="button"
                onClick={() => setNewTemplate('')}
                className={`text-left px-3 py-2 rounded-lg border text-sm flex items-center gap-2 ${newTemplate === '' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}`}
              >
                <LayoutTemplate className="h-4 w-4 text-gray-400" /> Écran vide
              </button>
              {templates.map((tpl) => (
                <button
                  key={tpl.id}
                  type="button"
                  onClick={() => setNewTemplate(tpl.id)}
                  className={`text-left px-3 py-2 rounded-lg border text-sm ${newTemplate === tpl.id ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}`}
                >
                  <div className="flex items-center gap-2 font-medium"><LayoutTemplate className="h-4 w-4 text-blue-500" /> {tpl.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5 ml-6">{tpl.description}</div>
                </button>
              ))}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewDialog(false)}>Annuler</Button>
            <Button onClick={createScreen} disabled={!newName.trim()}>Créer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog réglages écran (thème + en-tête) */}
      <Dialog open={showSettingsDialog} onOpenChange={setShowSettingsDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Réglages de l'écran</DialogTitle></DialogHeader>
          {screen && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Thème</Label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => { setScreen((p) => ({ ...p, theme: 'dark' })); setDirty(true); }}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-sm ${(screen.theme || 'dark') === 'dark' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}`}
                  >
                    <Moon className="h-4 w-4" /> Sombre
                  </button>
                  <button
                    type="button"
                    onClick={() => { setScreen((p) => ({ ...p, theme: 'light' })); setDirty(true); }}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-sm ${screen.theme === 'light' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}`}
                  >
                    <Sun className="h-4 w-4" /> Clair
                  </button>
                </div>
              </div>
              <div className="space-y-2 border-t pt-3">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={!!screen.header?.enabled}
                    onChange={(e) => { setScreen((p) => ({ ...p, header: { ...(p.header || {}), enabled: e.target.checked } })); setDirty(true); }}
                  />
                  Afficher un bandeau d'en-tête (logo, nom du site, horloge)
                </label>
                {screen.header?.enabled && (
                  <div className="space-y-2 pl-1">
                    <Input
                      value={screen.header?.title || ''}
                      onChange={(e) => { setScreen((p) => ({ ...p, header: { ...(p.header || {}), title: e.target.value } })); setDirty(true); }}
                      placeholder="Nom du site (ex: Atelier Production)"
                    />
                    <Input
                      value={screen.header?.logo_url || ''}
                      onChange={(e) => { setScreen((p) => ({ ...p, header: { ...(p.header || {}), logo_url: e.target.value } })); setDirty(true); }}
                      placeholder="URL du logo (optionnel)"
                    />
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500">N'oubliez pas de cliquer sur "Enregistrer" pour appliquer ces réglages.</p>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setShowSettingsDialog(false)}>Fermer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Aperçu plein écran */}
      {showFullscreenPreview && screen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: THEMES[screen.theme || 'dark'].pageBg }}>
          <button
            onClick={() => setShowFullscreenPreview(false)}
            style={{ position: 'absolute', top: 16, right: 16, zIndex: 101, background: 'rgba(0,0,0,.4)', border: 'none', borderRadius: 999, width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
          >
            <X size={18} color="#fff" />
          </button>
          <FullscreenPreview screen={screen} />
        </div>
      )}

      {/* Dialog lien public */}
      <Dialog open={showLinkDialog} onOpenChange={setShowLinkDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Lien public — {screen?.nom}</DialogTitle></DialogHeader>
          <p className="text-sm text-gray-500">
            Ce lien affiche l'écran en lecture seule, sans authentification. À utiliser dans votre application
            de signalétique (Yodeck, OptiSigns, navigateur en mode kiosque…). Ne le partagez qu'aux appareils de confiance.
          </p>
          <div className="flex items-center gap-2">
            <Input readOnly value={publicUrl} />
            <Button variant="outline" size="icon" onClick={copyLink}><Copy className="h-4 w-4" /></Button>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={regenerateToken}><RefreshCw className="h-4 w-4 mr-1" /> Régénérer le lien</Button>
            <Button onClick={() => setShowLinkDialog(false)}>Fermer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function FullscreenPreview({ screen }) {
  const [scale, setScale] = useState(1);
  const ref = useRef(null);
  const theme = THEMES[screen.theme || 'dark'];

  useEffect(() => {
    const update = () => {
      if (!ref.current) return;
      const { clientWidth, clientHeight } = ref.current;
      setScale(Math.min(clientWidth / DESIGN_W, clientHeight / DESIGN_H));
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  return (
    <div ref={ref} style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <div style={{ width: DESIGN_W, height: DESIGN_H, transform: `scale(${scale})`, transformOrigin: 'top left', position: 'relative' }}>
        {screen.blocks.map((block) => (
          <div
            key={block.id}
            className={isBlockInAlert(block) ? 'ad-alert-border' : ''}
            style={{
              position: 'absolute', left: block.x, top: block.y, width: block.w, height: block.h,
              background: theme.tileBg, border: `1px solid ${theme.tileBorder}`, borderRadius: 20, overflow: 'hidden',
            }}
          >
            <BlockContent block={block} theme={screen.theme || 'dark'} />
          </div>
        ))}
      </div>
    </div>
  );
}

function BlockInspector({ block, machines, sensors, equipments, onChange }) {
  const def = BLOCK_TYPES.find((t) => t.type === block.type);
  const config = block.config || {};

  return (
    <div className="space-y-4">
      <div className="text-sm font-semibold text-gray-800">{def?.label}</div>

      {block.type === 'cadence' && (
        <div className="space-y-2">
          <Label>Équipement</Label>
          <Select value={config.machine_id || ''} onValueChange={(v) => onChange({ machine_id: v })}>
            <SelectTrigger><SelectValue placeholder="Choisir un équipement" /></SelectTrigger>
            <SelectContent>
              {machines.map((m) => <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      )}

      {block.type === 'mqtt_sensor' && (
        <div className="space-y-2">
          <Label>Capteur</Label>
          <Select value={config.sensor_id || ''} onValueChange={(v) => onChange({ sensor_id: v })}>
            <SelectTrigger><SelectValue placeholder="Choisir un capteur" /></SelectTrigger>
            <SelectContent>
              {sensors.map((s) => <SelectItem key={s.id} value={s.id}>{s.nom}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      )}

      {block.type === 'free_text' && (
        <div className="space-y-2">
          <Label>Texte</Label>
          <Textarea rows={5} value={config.text || ''} onChange={(e) => onChange({ text: e.target.value })} />
        </div>
      )}

      {block.type === 'image' && (
        <div className="space-y-2">
          <Label>URL de l'image</Label>
          <Input value={config.url || ''} onChange={(e) => onChange({ url: e.target.value })} placeholder="https://…" />
        </div>
      )}

      {block.type === 'clock' && (
        <div className="space-y-2">
          <Label>Libellé (optionnel)</Label>
          <Input value={config.label || ''} onChange={(e) => onChange({ label: e.target.value })} placeholder="Ex: Heure locale" />
        </div>
      )}

      {block.type === 'equipment_status' && (
        <div className="space-y-2">
          <Label>Équipements à afficher</Label>
          <div className="border rounded-lg max-h-64 overflow-y-auto divide-y">
            {equipments.map((eq) => {
              const checked = (config.equipment_ids || []).includes(eq.id);
              return (
                <label key={eq.id} className="flex items-center gap-2 px-2 py-1.5 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => {
                      const current = config.equipment_ids || [];
                      const next = e.target.checked ? [...current, eq.id] : current.filter((id) => id !== eq.id);
                      onChange({ equipment_ids: next });
                    }}
                  />
                  {eq.nom}
                </label>
              );
            })}
          </div>
        </div>
      )}

      {block.type === 'work_orders' && (
        <div className="space-y-3">
          <div className="space-y-2">
            <Label>Nombre d'ordres affichés</Label>
            <Input type="number" min={1} max={20} value={config.limit ?? 5} onChange={(e) => onChange({ limit: parseInt(e.target.value, 10) || 5 })} />
          </div>
          <div className="space-y-2">
            <Label>Filtrer par équipement (optionnel)</Label>
            <Select value={config.equipment_id || '__all__'} onValueChange={(v) => onChange({ equipment_id: v === '__all__' ? '' : v })}>
              <SelectTrigger><SelectValue placeholder="Tous les équipements" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">Tous les équipements</SelectItem>
                {equipments.map((eq) => <SelectItem key={eq.id} value={eq.id}>{eq.nom}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {block.type === 'kpi' && (
        <div className="space-y-3">
          <div className="space-y-2">
            <Label>Équipement</Label>
            <Select value={config.machine_id || ''} onValueChange={(v) => onChange({ machine_id: v })}>
              <SelectTrigger><SelectValue placeholder="Choisir un équipement" /></SelectTrigger>
              <SelectContent>
                {machines.map((m) => <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Indicateur</Label>
            <Select value={config.metric || 'trs'} onValueChange={(v) => onChange({ metric: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {KPI_METRICS.map((m) => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {block.type === 'qrcode' && (
        <div className="space-y-3">
          <div className="space-y-2">
            <Label>Contenu (URL ou texte)</Label>
            <Input value={config.content || ''} onChange={(e) => onChange({ content: e.target.value })} placeholder="https://…" />
          </div>
          <div className="space-y-2">
            <Label>Légende (optionnel)</Label>
            <Input value={config.label || ''} onChange={(e) => onChange({ label: e.target.value })} placeholder="Ex: Scannez pour signaler un incident" />
          </div>
        </div>
      )}

      {block.type === 'ticker' && (
        <div className="space-y-3">
          <div className="space-y-2">
            <Label>Texte du bandeau</Label>
            <Textarea rows={3} value={config.text || ''} onChange={(e) => onChange({ text: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Vitesse de défilement</Label>
            <Select value={config.speed || 'normal'} onValueChange={(v) => onChange({ speed: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="lent">Lente</SelectItem>
                <SelectItem value="normal">Normale</SelectItem>
                <SelectItem value="rapide">Rapide</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}
    </div>
  );
}
