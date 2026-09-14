import React, { useState, useRef } from 'react';
import { Camera, Paperclip, X, ChevronLeft, Loader2, CheckCircle2, ShieldAlert, Send, Upload, CloudOff } from 'lucide-react';
import { BACKEND_URL } from '../../utils/config';
import { addToSyncQueue, storeOfflineFile, attachPendingFilesToLastQueueItem } from '../../services/offlineDb';

const API_URL = BACKEND_URL;
const FETCH_TIMEOUT_MS = 10000;

const fetchWithTimeout = (url, options = {}) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(timer));
};

const SEVERITIES = [
  { value: 'FAIBLE', label: 'Faible', color: 'bg-blue-50 text-blue-700 border-blue-200', ring: 'ring-blue-400' },
  { value: 'MOYEN', label: 'Moyen', color: 'bg-amber-50 text-amber-700 border-amber-200', ring: 'ring-amber-400' },
  { value: 'ELEVE', label: 'Eleve', color: 'bg-orange-50 text-orange-700 border-orange-200', ring: 'ring-orange-400' },
  { value: 'CRITIQUE', label: 'Critique', color: 'bg-red-50 text-red-700 border-red-200', ring: 'ring-red-400' },
];

const PublicPresquAccidentForm = ({ equipment, onClose }) => {
  const [step, setStep] = useState('form'); // form | sending | success | offline | error
  const [form, setForm] = useState({
    declarant: '',
    titre: '',
    description: '',
    severite: 'MOYEN',
  });
  const [photos, setPhotos] = useState([]);
  const [previewImg, setPreviewImg] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0);
  const cameraRef = useRef(null);
  const fileRef = useRef(null);
  const submittingRef = useRef(false);

  const handlePhoto = (e) => {
    const files = Array.from(e.target.files || []);
    const valid = files.filter(f => f.size <= 25 * 1024 * 1024);
    const newPhotos = valid.map(f => ({
      file: f,
      name: f.name,
      preview: URL.createObjectURL(f),
    }));
    setPhotos(prev => [...prev, ...newPhotos]);
    e.target.value = '';
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    dragCounter.current = 0;
    const files = Array.from(e.dataTransfer.files || []);
    if (files.length === 0) return;
    const valid = files.filter(f => f.size <= 25 * 1024 * 1024);
    const newPhotos = valid.map(f => ({
      file: f,
      name: f.name,
      preview: URL.createObjectURL(f),
    }));
    setPhotos(prev => [...prev, ...newPhotos]);
  };

  const removePhoto = (idx) => {
    URL.revokeObjectURL(photos[idx].preview);
    setPhotos(prev => prev.filter((_, i) => i !== idx));
  };

  // Compress image on client side before upload (for mobile compatibility)
  const compressImage = (file, maxSize = 1200, quality = 0.8) => {
    return new Promise((resolve) => {
      if (!file.type.startsWith('image/')) {
        resolve(file);
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        let { width, height } = img;

        if (Math.max(width, height) > maxSize) {
          if (width > height) {
            height = Math.round(height * (maxSize / width));
            width = maxSize;
          } else {
            width = Math.round(width * (maxSize / height));
            height = maxSize;
          }
        }

        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressed = new File([blob], file.name || 'photo.jpg', { type: 'image/jpeg' });
              resolve(compressed);
            } else {
              resolve(file);
            }
          },
          'image/jpeg',
          quality
        );
      };

      img.onerror = () => resolve(file);
      img.src = URL.createObjectURL(file);
    });
  };

  const queueOffline = async (payload) => {
    try {
      await addToSyncQueue('post', '/qr/public/presqu-accident', payload, {}, []);

      if (photos.length > 0) {
        const fileRefs = [];
        for (const photo of photos) {
          const fileId = `offline_qr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          try {
            await storeOfflineFile(fileId, photo.file, {
              name: photo.file.name || photo.name,
              type: photo.file.type,
              size: photo.file.size,
            });
            fileRefs.push({ fileId, name: photo.file.name || photo.name, type: photo.file.type });
          } catch (e) {
            console.warn('[Offline] Erreur stockage photo:', e);
          }
        }
        if (fileRefs.length > 0) {
          await attachPendingFilesToLastQueueItem('post', '/qr/public/presqu-accident', fileRefs);
        }
      }
      setStep('offline');
    } catch (e) {
      console.error('[Offline] Erreur mise en file d\'attente:', e);
      setErrorMsg('Impossible d\'enregistrer la declaration, meme hors ligne. Reessayez.');
      setStep('error');
    }
  };

  const handleSubmit = async () => {
    if (submittingRef.current) return;
    if (!form.titre.trim()) return setErrorMsg('Le titre est obligatoire');
    if (!form.description.trim()) return setErrorMsg('La description est obligatoire');
    submittingRef.current = true;
    setErrorMsg('');
    setStep('sending');

    const payload = {
      titre: form.titre.trim(),
      description: form.description.trim(),
      severite: form.severite,
      equipment_id: equipment.id,
      declarant: form.declarant.trim() || 'Anonyme',
    };

    // 1. Creer le presqu'accident
    let res;
    try {
      res = await fetchWithTimeout(`${API_URL}/api/qr/public/presqu-accident`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (networkErr) {
      // Vraie coupure reseau (ou delai depasse) : enregistrer localement pour envoi ulterieur
      await queueOffline(payload);
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      setErrorMsg(err.detail || 'Erreur serveur');
      setStep('error');
      submittingRef.current = false;
      return;
    }

    try {
      const result = await res.json();
      const itemId = result.id;

      // 2. Upload photos (compressed for mobile compatibility)
      for (const photo of photos) {
        try {
          const compressed = await compressImage(photo.file);
          const fd = new FormData();
          fd.append('file', compressed);
          const uploadRes = await fetchWithTimeout(`${API_URL}/api/qr/public/presqu-accident/${itemId}/attachments`, {
            method: 'POST',
            body: fd,
          });
          if (!uploadRes.ok) {
            console.warn('[QR] Photo upload failed:', uploadRes.status);
          }
        } catch (e) {
          console.warn('[QR] Photo upload error:', e);
        }
      }

      setStep('success');
    } catch (err) {
      setErrorMsg(err.message || 'Une erreur est survenue');
      setStep('error');
      submittingRef.current = false;
    }
  };

  // Success screen
  if (step === 'success') {
    return (
      <div className="space-y-6 text-center py-8" data-testid="public-pa-success">
        <div className="w-20 h-20 mx-auto rounded-full bg-emerald-100 flex items-center justify-center">
          <CheckCircle2 size={40} className="text-emerald-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Presqu'accident declare</h2>
          <p className="text-sm text-gray-500 mt-2">
            Merci pour votre vigilance. Votre declaration a ete transmise et sera examinee par l'equipe securite/maintenance.
          </p>
        </div>
        <button
          onClick={onClose}
          className="w-full py-3.5 rounded-xl bg-emerald-600 text-white font-semibold text-base active:bg-emerald-700 transition-colors"
          data-testid="public-pa-back-btn"
        >
          Retour a la fiche equipement
        </button>
      </div>
    );
  }

  // Offline screen
  if (step === 'offline') {
    return (
      <div className="space-y-6 text-center py-8" data-testid="public-pa-offline">
        <div className="w-20 h-20 mx-auto rounded-full bg-amber-100 flex items-center justify-center">
          <CloudOff size={40} className="text-amber-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Enregistre localement</h2>
          <p className="text-sm text-gray-500 mt-2">
            Pas de connexion pour le moment. Votre declaration est enregistree sur ce telephone et sera envoyee automatiquement des que le reseau revient.
          </p>
        </div>
        <button
          onClick={onClose}
          className="w-full py-3.5 rounded-xl bg-amber-600 text-white font-semibold text-base active:bg-amber-700 transition-colors"
          data-testid="public-pa-offline-back-btn"
        >
          Retour a la fiche equipement
        </button>
      </div>
    );
  }

  // Error screen
  if (step === 'error') {
    return (
      <div className="space-y-6 text-center py-8" data-testid="public-pa-error">
        <div className="w-20 h-20 mx-auto rounded-full bg-red-100 flex items-center justify-center">
          <ShieldAlert size={40} className="text-red-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Erreur</h2>
          <p className="text-sm text-gray-500 mt-2">{errorMsg}</p>
        </div>
        <div className="space-y-3">
          <button
            onClick={() => setStep('form')}
            className="w-full py-3.5 rounded-xl bg-blue-600 text-white font-semibold text-base active:bg-blue-700"
          >
            Reessayer
          </button>
          <button
            onClick={onClose}
            className="w-full py-3 rounded-xl border border-gray-300 text-gray-700 font-medium text-sm active:bg-gray-50"
          >
            Annuler
          </button>
        </div>
      </div>
    );
  }

  // Sending screen
  if (step === 'sending') {
    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-4" data-testid="public-pa-sending">
        <Loader2 size={40} className="animate-spin text-amber-600" />
        <p className="text-sm text-gray-600 font-medium">Envoi en cours...</p>
        {photos.length > 0 && (
          <p className="text-xs text-gray-400">Upload de {photos.length} photo(s)...</p>
        )}
      </div>
    );
  }

  // Form
  return (
    <div className="space-y-5" data-testid="public-pa-form">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={onClose}
          className="p-2 -ml-2 rounded-lg active:bg-gray-100 transition-colors"
          data-testid="public-pa-close-btn"
        >
          <ChevronLeft size={22} className="text-gray-600" />
        </button>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-bold text-gray-900">Declarer un presqu'accident</h2>
          <p className="text-xs text-gray-500 truncate">
            {equipment.nom}
            {equipment.emplacement ? ` — ${equipment.emplacement}` : ''}
          </p>
        </div>
      </div>

      {/* Equipment info bar */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
          <ShieldAlert size={18} className="text-amber-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-amber-900 truncate">{equipment.nom}</p>
          <p className="text-xs text-amber-700">Aucun compte necessaire — quelques secondes suffisent</p>
        </div>
      </div>

      {/* Form fields */}
      <div className="space-y-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">Votre nom</label>
          <input
            type="text"
            data-testid="public-pa-name"
            value={form.declarant}
            onChange={e => setForm(f => ({ ...f, declarant: e.target.value }))}
            placeholder="Prenom Nom (facultatif)"
            className="w-full px-4 py-3 rounded-xl border border-gray-300 text-base focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white placeholder-gray-400"
            autoComplete="name"
          />
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">
            Que s'est-il passe ? <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            data-testid="public-pa-titre"
            value={form.titre}
            onChange={e => setForm(f => ({ ...f, titre: e.target.value }))}
            placeholder="Ex: Glissade pres du convoyeur"
            className="w-full px-4 py-3 rounded-xl border border-gray-300 text-base focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white placeholder-gray-400"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">
            Circonstances <span className="text-red-500">*</span>
          </label>
          <textarea
            data-testid="public-pa-description"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Decrivez ce qui s'est passe et ce qui aurait pu arriver..."
            rows={4}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 text-base focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white placeholder-gray-400 resize-none"
          />
        </div>

        {/* Severity */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Gravite si ca avait eu lieu</label>
          <div className="grid grid-cols-4 gap-2" data-testid="public-pa-severity">
            {SEVERITIES.map(s => (
              <button
                key={s.value}
                type="button"
                onClick={() => setForm(f => ({ ...f, severite: s.value }))}
                className={`py-2.5 px-2 rounded-xl border text-xs font-medium transition-all ${
                  form.severite === s.value
                    ? `${s.color} ring-2 ring-offset-1 ${s.ring}`
                    : 'bg-white border-gray-200 text-gray-500'
                }`}
                data-testid={`public-pa-sev-${s.value}`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Photos */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Photos</label>
          <input ref={cameraRef} type="file" accept="image/*" capture="environment" onChange={handlePhoto} className="hidden" />
          <input ref={fileRef} type="file" accept="image/*" multiple onChange={handlePhoto} className="hidden" />

          {/* Zone de drag & drop */}
          <div
            data-testid="public-pa-drop-zone"
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className={`relative rounded-xl border-2 border-dashed transition-colors duration-200 ${
              isDragging
                ? 'border-amber-500 bg-amber-50'
                : 'border-gray-200 bg-white'
            }`}
          >
            {isDragging && (
              <div className="absolute inset-0 z-10 flex flex-col items-center justify-center rounded-xl bg-amber-50/90">
                <Upload size={32} className="text-amber-500 mb-2" />
                <p className="text-sm font-medium text-amber-600">Deposez vos photos ici</p>
              </div>
            )}
            <div className="p-3">
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => cameraRef.current?.click()}
                  className="flex flex-col items-center justify-center py-4 rounded-xl border-2 border-dashed border-amber-300 bg-amber-50 active:bg-amber-100 transition-colors"
                  data-testid="public-pa-camera-btn"
                >
                  <Camera size={28} className="text-amber-600 mb-1" />
                  <span className="text-sm font-medium text-amber-700">Prendre photo</span>
                </button>
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="flex flex-col items-center justify-center py-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 active:bg-gray-100 transition-colors"
                  data-testid="public-pa-file-btn"
                >
                  <Paperclip size={28} className="text-gray-500 mb-1" />
                  <span className="text-sm font-medium text-gray-600">Galerie</span>
                </button>
              </div>
              <p className="text-xs text-gray-400 text-center mt-2">
                Glissez-deposez vos photos ici ou utilisez les boutons
              </p>
            </div>
          </div>

          {/* Photo thumbnails */}
          {photos.length > 0 && (
            <div className="grid grid-cols-3 gap-2 mt-3" data-testid="public-pa-photos">
              {photos.map((photo, idx) => (
                <div key={idx} className="relative aspect-square rounded-xl overflow-hidden border border-gray-200 bg-gray-100">
                  <img src={photo.preview} alt={photo.name} className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => setPreviewImg(photo.preview)}
                    className="absolute inset-0 bg-black/0 active:bg-black/30 transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => removePhoto(idx)}
                    className="absolute top-1 right-1 p-1 bg-black/60 rounded-full active:bg-black/80"
                    data-testid={`public-pa-remove-photo-${idx}`}
                  >
                    <X size={14} className="text-white" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {errorMsg && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700" data-testid="public-pa-form-error">
          {errorMsg}
        </div>
      )}

      {/* Submit */}
      <button
        type="button"
        onClick={handleSubmit}
        className="w-full py-4 rounded-xl bg-amber-600 text-white font-semibold text-base flex items-center justify-center gap-2 active:bg-amber-700 transition-colors shadow-lg shadow-amber-600/25"
        data-testid="public-pa-submit-btn"
      >
        <Send size={20} />
        Envoyer la declaration
      </button>

      {/* Fullscreen preview */}
      {previewImg && (
        <div
          className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center p-4"
          onClick={() => setPreviewImg(null)}
        >
          <button
            className="absolute top-4 right-4 p-2 bg-white/20 rounded-full active:bg-white/40"
            onClick={() => setPreviewImg(null)}
          >
            <X size={24} className="text-white" />
          </button>
          <img
            src={previewImg}
            alt="Preview"
            className="max-w-full max-h-full object-contain rounded-lg"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
};

export default PublicPresquAccidentForm;
