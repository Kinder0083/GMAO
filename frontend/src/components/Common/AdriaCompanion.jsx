import React, { useState, useRef, useCallback, useEffect } from 'react';
import { usePreferences } from '../../contexts/PreferencesContext';
import { DEFAULT_AVATAR } from './AdriaAvatar';
import { useAdriaAnimation } from './useAdriaAnimation';
import AIChatWidget from './AIChatWidget';

const SIZE = 112; // px - doit correspondre a la taille de l'image (w-28/h-28)
const MARGIN = 8; // marge minimale gardee avec le bord de l'ecran

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const defaultPosition = () => ({
  left: window.innerWidth - SIZE - 24,
  top: window.innerHeight - SIZE - 24,
});

/**
 * Adria posee en superposition sur l'ecran, toujours visible (pas seulement
 * quand la conversation est ouverte) - style assistant Office. Un clic sur le
 * personnage ouvre/ferme la conversation (bulle ancree a lui) ; un glisser
 * deplace le personnage n'importe ou sur l'ecran, position memorisee par
 * utilisateur (Personnalisation, ai_assistant_position en pourcentage de
 * l'ecran pour rester coherente quelle que soit la taille de fenetre).
 */
const AdriaCompanion = ({ chatOpen, onOpenChat, onCloseChat, initialContext, initialQuestion }) => {
  const { preferences, updatePreferences } = usePreferences();
  const aiAvatar = preferences?.ai_assistant_avatar || DEFAULT_AVATAR;
  const aiName = preferences?.ai_assistant_name || 'Adria';
  const [speaking, setSpeaking] = useState(false);
  const src = useAdriaAnimation(aiAvatar, `/assets/adria/${aiAvatar}.png`, speaking);

  const savedPosition = preferences?.ai_assistant_position;
  const [pos, setPos] = useState(null); // {left, top} en px

  const dragRef = useRef({ dragging: false, moved: false, startX: 0, startY: 0, originLeft: 0, originTop: 0 });

  // Calcule la position a l'ecran depuis la preference (pourcentage) ou le
  // coin bas-droit par defaut, et la recalcule si la fenetre est redimensionnee.
  useEffect(() => {
    const compute = () => {
      if (savedPosition && typeof savedPosition.xPct === 'number' && typeof savedPosition.yPct === 'number') {
        setPos({
          left: clamp(savedPosition.xPct * window.innerWidth, MARGIN, window.innerWidth - SIZE - MARGIN),
          top: clamp(savedPosition.yPct * window.innerHeight, MARGIN, window.innerHeight - SIZE - MARGIN),
        });
      } else {
        setPos(defaultPosition());
      }
    };
    compute();
    window.addEventListener('resize', compute);
    return () => window.removeEventListener('resize', compute);
  }, [savedPosition]);

  const persistPosition = useCallback((left, top) => {
    updatePreferences({
      ai_assistant_position: {
        xPct: clamp(left / window.innerWidth, 0, 1),
        yPct: clamp(top / window.innerHeight, 0, 1),
      },
    });
  }, [updatePreferences]);

  const handlePointerDown = (e) => {
    if (!pos) return;
    dragRef.current = {
      dragging: true, moved: false,
      startX: e.clientX, startY: e.clientY,
      originLeft: pos.left, originTop: pos.top,
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e) => {
    const d = dragRef.current;
    if (!d.dragging) return;
    const dx = e.clientX - d.startX;
    const dy = e.clientY - d.startY;
    if (!d.moved && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) d.moved = true;
    if (!d.moved) return;
    setPos({
      left: clamp(d.originLeft + dx, MARGIN, window.innerWidth - SIZE - MARGIN),
      top: clamp(d.originTop + dy, MARGIN, window.innerHeight - SIZE - MARGIN),
    });
  };

  const handlePointerUp = () => {
    const d = dragRef.current;
    if (!d.dragging) return;
    d.dragging = false;
    if (d.moved) {
      setPos((current) => {
        if (current) persistPosition(current.left, current.top);
        return current;
      });
    }
  };

  const handleClick = () => {
    // Un clic juste apres un glisser ne doit pas ouvrir/fermer la conversation.
    if (dragRef.current.moved) {
      dragRef.current.moved = false;
      return;
    }
    if (chatOpen) onCloseChat(); else onOpenChat();
  };

  if (!pos) return null;

  return (
    <>
      <button
        type="button"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onClick={handleClick}
        aria-label={`${chatOpen ? 'Fermer' : 'Ouvrir'} la conversation avec ${aiName} (glisser pour déplacer le personnage)`}
        title={aiName}
        data-testid="adria-companion"
        className="fixed z-[9998] cursor-grab active:cursor-grabbing bg-transparent border-none p-0 touch-none select-none"
        style={{ left: pos.left, top: pos.top, width: SIZE, height: SIZE }}
      >
        <img
          src={src}
          alt=""
          draggable={false}
          className="w-full h-full object-contain animate-adria-bob motion-reduce:animate-none pointer-events-none"
          style={{ filter: 'drop-shadow(0 10px 14px rgba(10,10,20,0.28))' }}
        />
      </button>

      {chatOpen && (
        <AIChatWidget
          isOpen={chatOpen}
          onClose={onCloseChat}
          initialContext={initialContext}
          initialQuestion={initialQuestion}
          onSpeakingChange={setSpeaking}
          anchor={{ left: pos.left, top: pos.top, size: SIZE }}
        />
      )}
    </>
  );
};

export default AdriaCompanion;
