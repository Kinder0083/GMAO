import React, { useState } from 'react';
import { usePreferences } from '../../contexts/PreferencesContext';
import { DEFAULT_AVATAR } from './AdriaAvatar';
import { useAdriaAnimation } from './useAdriaAnimation';
import AIChatWidget from './AIChatWidget';

/**
 * Adria posee en superposition sur l'ecran, toujours visible (pas seulement
 * quand la conversation est ouverte) - style assistant Office. Un clic sur le
 * personnage ouvre/ferme la conversation, affichee en bulle ancree a lui
 * plutot que dans une fenetre separee.
 */
const AdriaCompanion = ({ chatOpen, onOpenChat, onCloseChat, initialContext, initialQuestion }) => {
  const { preferences } = usePreferences();
  const aiAvatar = preferences?.ai_assistant_avatar || DEFAULT_AVATAR;
  const aiName = preferences?.ai_assistant_name || 'Adria';
  const [speaking, setSpeaking] = useState(false);

  const src = useAdriaAnimation(aiAvatar, `/assets/adria/${aiAvatar}.png`, speaking);

  return (
    <>
      <button
        type="button"
        onClick={() => (chatOpen ? onCloseChat() : onOpenChat())}
        aria-label={`${chatOpen ? 'Fermer' : 'Ouvrir'} la conversation avec ${aiName}`}
        title={aiName}
        data-testid="adria-companion"
        className="fixed bottom-6 right-6 w-28 h-28 z-[9998] cursor-pointer bg-transparent border-none p-0"
      >
        <img
          src={src}
          alt=""
          className="w-full h-full object-contain animate-adria-bob motion-reduce:animate-none"
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
        />
      )}
    </>
  );
};

export default AdriaCompanion;
