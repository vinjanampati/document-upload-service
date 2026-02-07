import React, { useState, useEffect } from 'react';
import { uploadDocument, getDefaultConfig } from '../services/api';
import ConfigPanel from './ConfigPanel';
import UploadResult from './UploadResult';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load default config on mount
    getDefaultConfig().then(setConfig).catch(console.error);
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file || !config) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const uploadResult = await uploadDocument(file, config);
      setResult(uploadResult);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Document Upload Service</h1>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>1. Select File</h2>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".txt,.md,.pdf,.docx,.html"
          style={styles.fileInput}
        />
        {file && (
          <div style={styles.fileInfo}>
            <strong>Selected:</strong> {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </div>
        )}
      </div>

      {config && (
        <ConfigPanel config={config} onChange={setConfig} />
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        style={{
          ...styles.uploadButton,
          opacity: !file || loading ? 0.5 : 1,
          cursor: !file || loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Processing...' : 'Upload and Process'}
      </button>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && <UploadResult result={result} />}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    textAlign: 'center',
    color: '#333',
    marginBottom: '30px',
  },
  section: {
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: '15px',
    color: '#555',
  },
  fileInput: {
    width: '100%',
    padding: '10px',
    fontSize: '16px',
  },
  fileInfo: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#e8f4f8',
    borderRadius: '4px',
  },
  uploadButton: {
    width: '100%',
    padding: '15px',
    fontSize: '18px',
    fontWeight: 'bold',
    color: 'white',
    backgroundColor: '#4CAF50',
    border: 'none',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  error: {
    padding: '15px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '8px',
    marginBottom: '20px',
  },
};

export default FileUpload;
