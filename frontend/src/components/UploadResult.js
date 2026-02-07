import React from 'react';

const UploadResult = ({ result }) => {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>✅ Upload Successful!</h2>

      <div style={styles.info}>
        <div style={styles.infoRow}>
          <strong>File:</strong> {result.filename}
        </div>
        <div style={styles.infoRow}>
          <strong>File ID:</strong> {result.file_id}
        </div>
        <div style={styles.infoRow}>
          <strong>Size:</strong> {(result.file_size / 1024).toFixed(2)} KB
        </div>
        <div style={styles.infoRow}>
          <strong>Total Chunks:</strong> {result.total_chunks}
        </div>
        <div style={styles.infoRow}>
          <strong>Chunking Strategy:</strong> {result.chunking_strategy}
        </div>
        <div style={styles.infoRow}>
          <strong>Embedding Model:</strong> {result.embedding_model}
        </div>
        <div style={styles.infoRow}>
          <strong>Collection:</strong> {result.collection_name}
        </div>
      </div>

      {result.chunks_preview && result.chunks_preview.length > 0 && (
        <div style={styles.preview}>
          <h3 style={styles.previewTitle}>Chunk Preview (first 3 chunks):</h3>
          {result.chunks_preview.map((chunk, index) => (
            <div key={index} style={styles.chunk}>
              <div style={styles.chunkHeader}>
                <strong>Chunk {index + 1}</strong>
                <span style={styles.chunkMeta}>
                  ({chunk.start_char}-{chunk.end_char})
                </span>
              </div>
              <div style={styles.chunkText}>{chunk.text}</div>
              {chunk.metadata && (
                <div style={styles.chunkMetadata}>
                  <strong>Metadata:</strong> {JSON.stringify(chunk.metadata, null, 2)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#e8f5e9',
    borderRadius: '8px',
    marginTop: '20px',
  },
  title: {
    marginTop: 0,
    color: '#2e7d32',
  },
  info: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  infoRow: {
    padding: '8px 0',
    borderBottom: '1px solid #e0e0e0',
  },
  preview: {
    marginTop: '20px',
  },
  previewTitle: {
    marginBottom: '15px',
    color: '#555',
  },
  chunk: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '15px',
    border: '1px solid #ddd',
  },
  chunkHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
    paddingBottom: '10px',
    borderBottom: '1px solid #e0e0e0',
  },
  chunkMeta: {
    color: '#888',
    fontSize: '12px',
  },
  chunkText: {
    padding: '10px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    fontFamily: 'monospace',
    fontSize: '13px',
    lineHeight: '1.5',
    whiteSpace: 'pre-wrap',
  },
  chunkMetadata: {
    marginTop: '10px',
    padding: '10px',
    backgroundColor: '#f0f0f0',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace',
  },
};

export default UploadResult;
