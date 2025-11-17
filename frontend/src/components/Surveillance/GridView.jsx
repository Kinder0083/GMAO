import React, { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  IconButton,
  Box,
  CircularProgress,
  Tooltip,
  Divider
} from '@mui/material';
import { Edit, Delete, CheckCircle, AttachFile } from '@mui/icons-material';
import CompleteSurveillanceDialog from './CompleteSurveillanceDialog';

const getStatusColor = (status) => {
  switch (status) {
    case 'REALISE': return 'success';
    case 'PLANIFIE': return 'info';
    case 'PLANIFIER': return 'warning';
    default: return 'default';
  }
};

const getStatusLabel = (status) => {
  switch (status) {
    case 'REALISE': return 'Réalisé';
    case 'PLANIFIE': return 'Planifié';
    case 'PLANIFIER': return 'À planifier';
    default: return status;
  }
};

const getCategoryLabel = (category) => {
  const labels = {
    MMRI: 'MMRI',
    INCENDIE: 'Incendie',
    SECURITE_ENVIRONNEMENT: 'Sécurité/Environnement',
    ELECTRIQUE: 'Électrique',
    MANUTENTION: 'Manutention',
    EXTRACTION: 'Extraction',
    AUTRE: 'Autre'
  };
  return labels[category] || category;
};

function GridView({ items, loading, onEdit, onDelete, onRefresh }) {
  const [completeDialog, setCompleteDialog] = useState({ open: false, item: null });

  const handleComplete = (item) => {
    setCompleteDialog({ open: true, item });
  };

  const handleCompleteClose = (shouldRefresh) => {
    setCompleteDialog({ open: false, item: null });
    if (shouldRefresh && onRefresh) {
      onRefresh();
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Grouper les items par catégorie
  const groupedItems = items.reduce((acc, item) => {
    const category = item.category || 'AUTRE';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {});

  const categories = Object.keys(groupedItems).sort();

  return (
    <>
      {categories.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">Aucun contrôle trouvé</Typography>
        </Box>
      ) : (
        categories.map((category) => (
          <Box key={category} sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              {getCategoryLabel(category)} ({groupedItems[category].length})
            </Typography>
            <Grid container spacing={2}>
              {groupedItems[category].map((item) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      border: item.status === 'REALISE' ? '2px solid #4caf50' : '1px solid #e0e0e0'
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold" sx={{ flex: 1 }}>
                          {item.classe_type}
                        </Typography>
                        <Chip
                          label={getStatusLabel(item.status)}
                          color={getStatusColor(item.status)}
                          size="small"
                        />
                      </Box>
                      
                      <Divider sx={{ my: 1 }} />
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Bâtiment:</strong> {item.batiment}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Périodicité:</strong> {item.periodicite}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Responsable:</strong> {item.responsable}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Exécutant:</strong> {item.executant}
                      </Typography>
                      
                      {item.prochain_controle && (
                        <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                          <strong>Prochain:</strong> {new Date(item.prochain_controle).toLocaleDateString('fr-FR')}
                        </Typography>
                      )}
                      
                      {item.piece_jointe_url && (
                        <Chip
                          icon={<AttachFile />}
                          label="Fichier joint"
                          size="small"
                          variant="outlined"
                          sx={{ mt: 1 }}
                        />
                      )}
                    </CardContent>
                    
                    <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                      <Box>
                        {item.status !== 'REALISE' && (
                          <Tooltip title="Marquer comme réalisé">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleComplete(item)}
                            >
                              <CheckCircle />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Modifier">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => onEdit(item)}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      <Tooltip title="Supprimer">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => onDelete(item.id)}
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        ))
      )}

      {completeDialog.open && (
        <CompleteSurveillanceDialog
          open={completeDialog.open}
          item={completeDialog.item}
          onClose={handleCompleteClose}
        />
      )}
    </>
  );
}

export default GridView;
