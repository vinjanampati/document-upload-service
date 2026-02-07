import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file, config) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('config_json', JSON.stringify(config));

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getCollections = async () => {
  const response = await api.get('/collections');
  return response.data;
};

export const getCollectionInfo = async (collectionName) => {
  const response = await api.get(`/collections/${collectionName}`);
  return response.data;
};

export const deleteCollection = async (collectionName) => {
  const response = await api.delete(`/collections/${collectionName}`);
  return response.data;
};

export const getDefaultConfig = async () => {
  const response = await api.get('/config/defaults');
  return response.data;
};

export default api;
