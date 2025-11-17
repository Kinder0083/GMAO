import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  CircularProgress,
  Box,
  Tooltip
} from '@mui/material';
import { Edit, Delete, CheckCircle, Schedule, Warning } from '@mui/icons-material';
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
    SECURITE_ENVIRONNEMENT: 'Sécurité/Env.',
    ELECTRIQUE: 'Électrique',
    MANUTENTION: 'Manutention',
    EXTRACTION: 'Extraction',
    AUTRE: 'Autre'
  };
  return labels[category] || category;
};

function ListView({ items, loading, onEdit, onDelete, onRefresh }) {
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

  return (
    <>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Catégorie</strong></TableCell>
              <TableCell><strong>Bâtiment</strong></TableCell>
              <TableCell><strong>Périodicité</strong></TableCell>
              <TableCell><strong>Responsable</strong></TableCell>
              <TableCell><strong>Exécutant</strong></TableCell>
              <TableCell><strong>Dernier contrôle</strong></TableCell>
              <TableCell><strong>Prochain contrôle</strong></TableCell>
              <TableCell><strong>Statut</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  Aucun contrôle trouvé
                </TableCell>
              </TableRow>
            ) : (
              items.map((item) => (
                <TableRow key={item.id} hover>
                  <TableCell>{item.classe_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={getCategoryLabel(item.category)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{item.batiment}</TableCell>
                  <TableCell>{item.periodicite}</TableCell>
                  <TableCell>{item.responsable}</TableCell>
                  <TableCell>{item.executant}</TableCell>
                  <TableCell>
                    {item.derniere_visite
                      ? new Date(item.derniere_visite).toLocaleDateString('fr-FR')
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {item.prochain_controle
                      ? new Date(item.prochain_controle).toLocaleDateString('fr-FR')
                      : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(item.status)}
                      color={getStatusColor(item.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
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
                      <Tooltip title="Supprimer">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => onDelete(item.id)}
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

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

export default ListView;
