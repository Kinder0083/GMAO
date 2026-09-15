import React from 'react';
import { Button } from '../ui/button';
import { usePreferences } from '../../contexts/PreferencesContext';
import { useAIContextMenu } from '../../contexts/AIContextMenuContext';
import AdriaAvatar, { DEFAULT_AVATAR } from './AdriaAvatar';

const AIButton = () => {
  const { preferences } = usePreferences();
  const { openChat, chatOpen } = useAIContextMenu();

  const aiName = preferences?.ai_assistant_name || 'Adria';
  const aiAvatar = preferences?.ai_assistant_avatar || DEFAULT_AVATAR;

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => openChat()}
      data-testid="ai-assistant-button"
      className={`gap-2 ${chatOpen ? 'bg-purple-100 border-purple-300' : 'bg-purple-50 hover:bg-purple-100'} text-purple-700 border-purple-200`}
      title={`Discuter avec ${aiName}`}
    >
      <AdriaAvatar variant={aiAvatar} size={18} />
      <span className="hidden md:inline">{aiName}</span>
    </Button>
  );
};

export default AIButton;
