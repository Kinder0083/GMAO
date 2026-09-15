import React, { useState, useEffect, useRef, useContext } from 'react';
import { X, Send, Loader2, Trash2, Mic, MicOff, Volume2, VolumeX, WifiOff } from 'lucide-react';
import { usePreferences } from '../../contexts/PreferencesContext';
import { useToast } from '../../hooks/use-toast';
import api from '../../services/api';
import GuidedHighlight from './GuidedHighlight';
import { AINavigationContext } from '../../contexts/AINavigationContext';
import { executeCommand } from './adriaCommandHandlers';
import useAdriaVoice from './useAdriaVoice';
import useOnlineStatus from '../../hooks/useOnlineStatus';

const QUICK_ACTIONS = [
  { id: 'creer-ot', label: 'Créer un OT', icon: '📋' },
  { id: 'creer-equipement', label: 'Ajouter équipement', icon: '🔧' },
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'capteurs', label: 'Capteurs IoT', icon: '📡' },
];

const ACTION_COMMAND_REGEX = /\[\[(CREATE_OT|MODIFY_OT|CLOSE_OT|ADD_TIME_OT|COMMENT_OT|SEARCH|CONFIGURE_AUTOMATION|CREATE_WIDGET):(\{[\s\S]*?\})\]\]/g;
const GUIDE_REGEX = /\[\[GUIDE_START:([^\]]+)\]\]\s*(\{[\s\S]*?\})\s*\[\[GUIDE_END\]\]/g;
const AUTO_TEXT_REGEX = /\[\[CONFIGURE_AUTOMATION:([^\]]+)\]\]/g;
const NAV_COMMAND_REGEX = /\[\[(NAVIGATE|ACTION|GUIDE|SPOTLIGHT|PULSE|TRAIL|TOOLTIP|CELEBRATE):([^\]]+)\]\]/g;

const ROUTE_MAP = {
  'dashboard': 'dashboard', 'work-orders': 'ordres-de-travail', 'assets': 'equipements',
  'locations': 'emplacements', 'inventory': 'inventaire', 'preventive-maintenance': 'maintenance-preventive',
  'sensors': 'capteurs', 'meters': 'compteurs', 'reports': 'rapports',
  'settings': 'parametres', 'personnalisation': 'personnalisation'
};

const GAP = 12; // ecart en px entre le personnage flottant et la bulle
const EDGE_MARGIN = 8;
const BUBBLE_WIDTH = 260;
const BUBBLE_HEIGHT_BUDGET = 300; // estimation large (nuage + actions + saisie) pour le calage vertical

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

// Positionne le petit panneau (actions rapides + saisie + bulle nuage) a
// cote du personnage flottant (qui peut etre n'importe ou a l'ecran depuis
// qu'il est deplacable) : a gauche s'il y a la place, sinon a droite, sinon
// centre. La bulle nuage reste toujours l'element le plus proche du
// personnage (voir l'ordre du JSX plus bas), sa pointe est donc visee vers
// le haut du corps du personnage plutot que son centre exact.
function computeCloudLayout(anchor) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const spaceLeft = anchor.left;
  const spaceRight = vw - (anchor.left + anchor.size);

  let left;
  let tailSide;
  if (spaceLeft >= BUBBLE_WIDTH + GAP) {
    left = anchor.left - GAP - BUBBLE_WIDTH;
    tailSide = 'right';
  } else if (spaceRight >= BUBBLE_WIDTH + GAP) {
    left = anchor.left + anchor.size + GAP;
    tailSide = 'left';
  } else {
    left = clamp(anchor.left + anchor.size / 2 - BUBBLE_WIDTH / 2, EDGE_MARGIN, vw - BUBBLE_WIDTH - EDGE_MARGIN);
    tailSide = null;
  }

  const bottomTarget = clamp(anchor.top + anchor.size * 0.62, EDGE_MARGIN + BUBBLE_HEIGHT_BUDGET, vh - EDGE_MARGIN);
  const top = clamp(bottomTarget - BUBBLE_HEIGHT_BUDGET, EDGE_MARGIN, vh - BUBBLE_HEIGHT_BUDGET - EDGE_MARGIN);
  return { left, top, tailSide };
}

// Contour "nuage BD" (scallope) + pointes gauche/droite - genere a partir de
// 9 points repartis sur une ellipse, relies par des courbes qui bombent vers
// l'exterieur. Symetrique horizontalement, donc un seul contour sert pour
// les deux orientations ; seule la pointe change de cote.
const CLOUD_PATH = 'M 140.0 27.0 Q 192.5 7.6 209.4 40.6 Q 272.8 43.8 246.4 74.9 Q 291.0 99.3 233.5 114.0 Q 238.6 148.1 176.9 139.5 Q 140.0 167.4 103.1 139.5 Q 41.4 148.1 46.5 114.0 Q -11.0 99.3 33.6 74.9 Q 7.2 43.8 70.6 40.6 Q 87.5 7.6 140.0 27.0 Z';
const TAIL_PATH_RIGHT = 'M 190 150 Q 210 175 230 185 Q 212 160 205 145 Z';
const TAIL_PATH_LEFT = 'M 90 150 Q 70 175 50 185 Q 68 160 75 145 Z';
const CLOUD_VIEWBOX_H = 190 / 310; // ratio hauteur/largeur du viewBox (-15 0 310 190)

const AIChatWidget = ({ isOpen, onClose, initialContext = null, initialQuestion = null, onSpeakingChange = null, anchor = null }) => {
  const { preferences } = usePreferences();
  const { toast } = useToast();
  const { isOnline } = useOnlineStatus();
  const navigationContext = useContext(AINavigationContext);
  const executeAction = navigationContext?.executeAction;
  const navigateTo = navigationContext?.navigateTo;
  const startGuidance = navigationContext?.startGuidance;

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [hasProcessedInitialQuestion, setHasProcessedInitialQuestion] = useState(false);
  const [activeGuide, setActiveGuide] = useState(null);
  const [layout, setLayout] = useState(null);

  const inputRef = useRef(null);
  const aiName = preferences?.ai_assistant_name || 'Adria';
  const aiGender = preferences?.ai_assistant_gender || 'female';

  // Hook vocal
  const handleTranscription = async (transcription) => {
    const userMessage = { role: 'user', content: `🎤 ${transcription}`, timestamp: new Date().toISOString(), isVoice: true };
    setMessages(prev => [...prev, userMessage]);
    setShowQuickActions(false);
    await sendMessageToAI(transcription);
  };
  const voice = useAdriaVoice({ toast, onTranscription: handleTranscription });

  // Anime les levres du personnage flottant : un court "burst" a chaque
  // nouveau message de l'assistant (duree proportionnelle a sa longueur),
  // prolonge tant que la voix (TTS) le lit a voix haute.
  const [textBurstActive, setTextBurstActive] = useState(false);
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!last || last.role !== 'assistant') return undefined;
    setTextBurstActive(true);
    const duration = Math.min(6000, Math.max(1200, last.content.length * 45));
    const t = setTimeout(() => setTextBurstActive(false), duration);
    return () => clearTimeout(t);
  }, [messages]);
  useEffect(() => {
    onSpeakingChange?.(textBurstActive || voice.isPlayingAudio);
  }, [textBurstActive, voice.isPlayingAudio, onSpeakingChange]);
  useEffect(() => () => onSpeakingChange?.(false), [onSpeakingChange]);

  // Position du panneau, ancree au personnage flottant (qui peut etre
  // n'importe ou a l'ecran depuis qu'il est deplacable).
  useEffect(() => {
    if (!anchor) { setLayout(null); return undefined; }
    const compute = () => setLayout(computeCloudLayout(anchor));
    compute();
    window.addEventListener('resize', compute);
    return () => window.removeEventListener('resize', compute);
  }, [anchor]);

  // Focus input
  useEffect(() => { if (isOpen && inputRef.current) setTimeout(() => inputRef.current?.focus(), 100); }, [isOpen]);
  // Message de bienvenue
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const greeting = aiGender === 'female'
        ? `Bonjour ! Je suis ${aiName}, votre assistante FSAO. Comment puis-je vous aider aujourd'hui ?`
        : `Bonjour ! Je suis ${aiName}, votre assistant FSAO. Comment puis-je vous aider aujourd'hui ?`;
      setMessages([{ role: 'assistant', content: greeting, timestamp: new Date().toISOString() }]);
      setHasProcessedInitialQuestion(false);
    }
  }, [isOpen, aiName, aiGender]);
  // Question initiale (menu contextuel)
  useEffect(() => {
    if (isOpen && initialQuestion && !hasProcessedInitialQuestion && messages.length > 0 && !loading) {
      setHasProcessedInitialQuestion(true);
      setShowQuickActions(false);
      setMessages(prev => [...prev, { role: 'user', content: initialQuestion, timestamp: new Date().toISOString() }]);
      sendMessageToAI(initialQuestion);
    }
  }, [isOpen, initialQuestion, hasProcessedInitialQuestion, messages.length, loading]);
  useEffect(() => { if (!isOpen) setHasProcessedInitialQuestion(false); }, [isOpen]);

  // ==================== Exécution des commandes IA ====================
  const executeAutoAction = async (actionType, actionData) => {
    try {
      const result = await executeCommand(actionType, actionData);
      if (result.toastTitle) toast({ title: result.toastTitle, description: result.toastDesc });
      if (result.message) {
        setMessages(prev => [...prev, {
          role: 'assistant', content: result.message,
          timestamp: new Date().toISOString(), isSystemAction: true
        }]);
      }
    } catch (error) {
      console.error('Erreur action automatique:', error);
      toast({ title: 'Erreur', description: `Impossible d'exécuter l'action: ${error.message}`, variant: 'destructive' });
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Désolé, une erreur est survenue : ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toISOString(), isSystemAction: true
      }]);
    }
  };

  // ==================== Parsing des commandes dans la réponse IA ====================
  const parseAndExecuteCommands = (responseText) => {
    // Guides pas à pas
    let guideMatch = GUIDE_REGEX.exec(responseText);
    GUIDE_REGEX.lastIndex = 0;
    if (guideMatch) {
      try {
        const guideData = JSON.parse(guideMatch[2]);
        setActiveGuide({ name: guideMatch[1], title: guideData.title || 'Guide interactif', steps: guideData.steps || [] });
        toast({ title: 'Guide démarré', description: guideData.title || 'Suivez les étapes en surbrillance' });
      } catch (e) { console.error('Erreur parsing guide:', e); }
    }

    // Actions automatiques (CREATE_OT, MODIFY_OT, CLOSE_OT, etc.)
    let actionMatch;
    const actionRegex = new RegExp(ACTION_COMMAND_REGEX.source, 'g');
    while ((actionMatch = actionRegex.exec(responseText)) !== null) {
      try {
        executeAutoAction(actionMatch[1], JSON.parse(actionMatch[2]));
      } catch (e) { console.error('Erreur parsing action:', e); }
    }

    // Automation texte libre
    const autoRegex = new RegExp(AUTO_TEXT_REGEX.source, 'g');
    let autoTextMatch;
    while ((autoTextMatch = autoRegex.exec(responseText)) !== null) {
      const msg = autoTextMatch[1].trim();
      if (!msg.startsWith('{')) executeAutoAction('CONFIGURE_AUTOMATION', { message: msg });
    }

    // Commandes de navigation
    const navRegex = new RegExp(NAV_COMMAND_REGEX.source, 'g');
    let match;
    const commands = [];
    while ((match = navRegex.exec(responseText)) !== null) {
      commands.push({ type: match[1], action: match[2] });
    }

    // Nettoyer le texte affiché
    let cleanText = responseText
      .replace(GUIDE_REGEX, '').replace(ACTION_COMMAND_REGEX, '')
      .replace(AUTO_TEXT_REGEX, '').replace(NAV_COMMAND_REGEX, '').trim();

    if (commands.length > 0) {
      setTimeout(() => executeNavCommands(commands), 1000);
    }
    return cleanText;
  };

  const executeNavCommands = (commands) => {
    commands.forEach(cmd => {
      if (cmd.type === 'NAVIGATE' && navigateTo) {
        navigateTo(ROUTE_MAP[cmd.action] || cmd.action);
        toast({ title: 'Navigation', description: `Je vous emmène vers ${cmd.action.replace('-', ' ')}...` });
      } else if (cmd.type === 'ACTION' && executeAction) {
        executeAction(cmd.action);
      } else if (cmd.type === 'GUIDE' && startGuidance) {
        if (startGuidance(cmd.action)) onClose();
      } else if (cmd.type === 'SPOTLIGHT' && navigationContext?.showSpotlight) {
        navigationContext.showSpotlight(cmd.action);
      } else if (cmd.type === 'PULSE' && navigationContext?.addPulseEffect) {
        navigationContext.addPulseEffect(cmd.action);
      } else if (cmd.type === 'TRAIL' && navigationContext?.showTrail) {
        const [s, e] = cmd.action.split(':');
        if (s && e) navigationContext.showTrail(s, e);
      } else if (cmd.type === 'TOOLTIP' && navigationContext?.showCustomTooltip) {
        const [sel, ...parts] = cmd.action.split(':');
        if (sel && parts.length) navigationContext.showCustomTooltip(sel, parts.join(':'));
      } else if (cmd.type === 'CELEBRATE' && navigationContext?.celebrate) {
        navigationContext.celebrate();
      }
    });
  };

  // ==================== Envoi de message ====================
  const sendMessageToAI = async (messageContent) => {
    setLoading(true);
    try {
      const context = initialContext || `Page actuelle: ${window.location.pathname}`;
      const response = await api.ai.chat({ message: messageContent, session_id: sessionId, context });
      const cleanResponse = parseAndExecuteCommands(response.data.response);
      setMessages(prev => [...prev, { role: 'assistant', content: cleanResponse, timestamp: new Date().toISOString() }]);
      setSessionId(response.data.session_id);
      if (voice.isTTSEnabled && cleanResponse) voice.speakText(cleanResponse);
    } catch (error) {
      console.error('Erreur chat IA:', error);
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Désolé, je rencontre des difficultés techniques. ${error.response?.data?.detail || 'Veuillez réessayer.'}`,
        timestamp: new Date().toISOString(), error: true
      }]);
      toast({ title: 'Erreur', description: 'Impossible de contacter l\'assistant IA', variant: 'destructive' });
    } finally { setLoading(false); }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    setShowQuickActions(false);
    setMessages(prev => [...prev, { role: 'user', content: input.trim(), timestamp: new Date().toISOString() }]);
    const msg = input.trim();
    setInput('');
    await sendMessageToAI(msg);
  };

  const handleQuickAction = async (actionId) => {
    setShowQuickActions(false);
    const action = QUICK_ACTIONS.find(a => a.id === actionId);
    if (!action) return;
    setMessages(prev => [...prev, { role: 'user', content: `${action.icon} ${action.label}`, timestamp: new Date().toISOString(), isQuickAction: true }]);
    if (executeAction) {
      try {
        await executeAction(actionId);
        setMessages(prev => [...prev, { role: 'assistant', content: `Je vous ai dirigé vers "${action.label}". Que puis-je faire d'autre ?`, timestamp: new Date().toISOString() }]);
      } catch {
        setMessages(prev => [...prev, { role: 'assistant', content: `Je n'ai pas pu naviguer vers "${action.label}".`, timestamp: new Date().toISOString() }]);
      }
    } else {
      setMessages(prev => [...prev, { role: 'assistant', content: `Pour accéder à "${action.label}", utilisez le menu latéral.`, timestamp: new Date().toISOString() }]);
    }
  };

  const handleClearHistory = async () => {
    if (sessionId) { try { await api.ai.clearHistory(sessionId); } catch {} }
    setMessages([]); setSessionId(null); setShowQuickActions(true);
    toast({ title: 'Historique effacé', description: 'La conversation a été réinitialisée' });
  };

  if (!isOpen || !layout) return null;

  const lastMessage = messages[messages.length - 1] || null;
  const cloudIsUser = !loading && lastMessage?.role === 'user';
  const cloudIsError = !loading && Boolean(lastMessage?.error);
  const cloudKey = loading ? `loading-${messages.length}` : `msg-${messages.length}`;
  const tailPath = layout.tailSide === 'left' ? TAIL_PATH_LEFT : layout.tailSide === 'right' ? TAIL_PATH_RIGHT : null;
  const bubbleFill = cloudIsError ? '#fef2f2' : cloudIsUser ? '#7c3aed' : '#ffffff';
  const bubbleStroke = cloudIsError ? '#dc2626' : '#5b21b6';
  const textColor = cloudIsUser && !cloudIsError ? '#ffffff' : '#1e2433';
  const bubbleHeight = Math.round(BUBBLE_WIDTH * CLOUD_VIEWBOX_H);

  return (
    <div className="fixed flex flex-col items-end gap-2" style={{ left: layout.left, top: layout.top, width: BUBBLE_WIDTH, zIndex: 9999 }} data-testid="adria-chat-widget">
      {/* Barre utilitaire minimale - pas d'en-tete plein, le personnage juste a cote joue deja ce role */}
      <div className="flex items-center gap-1.5">
        {!isOnline && <span className="text-red-500" title="Hors ligne"><WifiOff size={13} /></span>}
        <button onClick={handleClearHistory} className="p-1.5 rounded-full bg-white hover:bg-gray-100 text-gray-500 shadow" title="Effacer l'historique" data-testid="adria-clear-btn">
          <Trash2 size={13} />
        </button>
        <button onClick={onClose} className="p-1.5 rounded-full bg-white hover:bg-gray-100 text-gray-500 shadow" title="Fermer" data-testid="adria-close-btn">
          <X size={13} />
        </button>
      </div>

      {showQuickActions && messages.length <= 1 && (
        <div className="flex flex-wrap gap-1.5 justify-end" data-testid="adria-quick-actions">
          {QUICK_ACTIONS.map(action => (
            <button key={action.id} onClick={() => handleQuickAction(action.id)} data-testid={`quick-action-${action.id}`}
              className="flex items-center gap-1 px-2.5 py-1 bg-white hover:bg-purple-50 text-purple-700 border border-purple-200 rounded-full text-xs font-medium shadow-sm transition-colors">
              <span>{action.icon}</span><span>{action.label}</span>
            </button>
          ))}
        </div>
      )}

      <div className="w-full">
        <div className="flex items-center gap-1 bg-white rounded-full shadow-lg pl-3 pr-1 py-1">
          <button onClick={voice.isRecording ? voice.stopRecording : voice.startRecording} disabled={loading}
            className={`p-1.5 rounded-full flex-shrink-0 transition-colors ${voice.isRecording ? 'bg-red-500 text-white animate-pulse' : 'text-gray-500 hover:bg-gray-100'}`}
            data-testid="adria-mic-btn">
            {voice.isRecording ? <MicOff size={15} /> : <Mic size={15} />}
          </button>
          <input ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleSend(); } }}
            placeholder={voice.isRecording ? 'Enregistrement…' : `Réponds à ${aiName}…`}
            className="flex-1 min-w-0 text-sm border-none outline-none bg-transparent"
            disabled={loading || voice.isRecording} data-testid="adria-input" />
          <button onClick={() => voice.setIsTTSEnabled(!voice.isTTSEnabled)} data-testid="adria-tts-toggle"
            className={`p-1.5 rounded-full flex-shrink-0 transition-colors ${voice.isTTSEnabled ? 'text-purple-600' : 'text-gray-400'}`} title="Voix">
            {voice.isTTSEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
          </button>
          <button onClick={handleSend} disabled={!input.trim() || loading || voice.isRecording}
            className="p-1.5 rounded-full bg-purple-600 text-white disabled:opacity-40 flex-shrink-0" data-testid="adria-send-btn">
            {loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
          </button>
        </div>
        {voice.isPlayingAudio && (
          <div className="flex justify-end mt-1">
            <button onClick={voice.stopAudio} className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700" data-testid="adria-stop-audio">Arrêter la voix</button>
          </div>
        )}
        {voice.isRecording && (
          <div className="flex justify-end mt-1">
            <span className="text-xs px-2 py-0.5 rounded-full bg-red-50 text-red-600">🔴 Parlez, recliquez le micro pour terminer</span>
          </div>
        )}
      </div>

      {/* Bulle nuage - toujours l'element le plus proche du personnage, pour
          que sa pointe reste visee vers lui quelle que soit la conversation */}
      <div className="relative" style={{ width: BUBBLE_WIDTH, height: bubbleHeight }} data-testid="adria-messages">
        <svg viewBox="-15 0 310 190" width={BUBBLE_WIDTH} height={bubbleHeight} style={{ display: 'block', overflow: 'visible' }}>
          {tailPath && <path d={tailPath} style={{ fill: bubbleFill, stroke: bubbleStroke, strokeWidth: 5, strokeLinejoin: 'round' }} />}
          <path d={CLOUD_PATH} style={{ fill: bubbleFill, stroke: bubbleStroke, strokeWidth: 5, strokeLinejoin: 'round' }} />
        </svg>
        <div key={cloudKey} className="absolute flex flex-col justify-start items-center text-center px-1 overflow-y-auto animate-cloud-in"
             style={{ left: '12.3%', top: '20%', width: '67.7%', height: '50%', fontSize: 12.5, lineHeight: 1.4, color: textColor, fontFamily: '"Comfortaa", sans-serif' }}>
          {loading ? (
            <span className="flex items-center gap-1.5 text-gray-500" style={{ fontFamily: 'inherit' }}>
              <Loader2 size={14} className="animate-spin" />{aiName} réfléchit…
            </span>
          ) : (
            <span className="whitespace-pre-wrap">{lastMessage?.content || ''}</span>
          )}
        </div>
      </div>

      {activeGuide && (
        <GuidedHighlight guide={activeGuide}
          onComplete={() => { setActiveGuide(null); toast({ title: 'Guide terminé !', description: 'Vous avez complété toutes les étapes.' }); setMessages(prev => [...prev, { role: 'assistant', content: 'Bravo ! Guide terminé.', timestamp: new Date().toISOString() }]); }}
          onCancel={() => { setActiveGuide(null); toast({ title: 'Guide annulé' }); }}
          onStepChange={(step) => console.log('Étape du guide:', step)} />
      )}
    </div>
  );
};

export default AIChatWidget;
