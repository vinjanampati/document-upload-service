import React from 'react';

const ConfigPanel = ({ config, onChange }) => {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div style={styles.section}>
      <h2 style={styles.sectionTitle}>2. Configure Chunking & Embedding</h2>

      <div style={styles.grid}>
        {/* Chunking Strategy */}
        <div style={styles.field}>
          <label style={styles.label}>Chunking Strategy:</label>
          <select
            value={config.chunking_strategy}
            onChange={(e) => handleChange('chunking_strategy', e.target.value)}
            style={styles.select}
          >
            <option value="fixed">Fixed (with overlap)</option>
            <option value="semantic">Semantic (similarity-based)</option>
            <option value="hierarchical">Hierarchical (parent+child)</option>
          </select>
        </div>

        {/* Chunk Size */}
        {config.chunking_strategy !== 'hierarchical' && (
          <div style={styles.field}>
            <label style={styles.label}>Chunk Size:</label>
            <input
              type="number"
              value={config.chunk_size}
              onChange={(e) => handleChange('chunk_size', parseInt(e.target.value))}
              min="100"
              max="4000"
              style={styles.input}
            />
          </div>
        )}

        {/* Chunk Overlap */}
        {config.chunking_strategy === 'fixed' && (
          <div style={styles.field}>
            <label style={styles.label}>Chunk Overlap:</label>
            <input
              type="number"
              value={config.chunk_overlap}
              onChange={(e) => handleChange('chunk_overlap', parseInt(e.target.value))}
              min="0"
              max="500"
              style={styles.input}
            />
          </div>
        )}

        {/* Hierarchical Settings */}
        {config.chunking_strategy === 'hierarchical' && (
          <>
            <div style={styles.field}>
              <label style={styles.label}>Parent Chunk Size:</label>
              <input
                type="number"
                value={config.parent_chunk_size}
                onChange={(e) => handleChange('parent_chunk_size', parseInt(e.target.value))}
                min="1000"
                max="8000"
                style={styles.input}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Child Chunk Size:</label>
              <input
                type="number"
                value={config.child_chunk_size}
                onChange={(e) => handleChange('child_chunk_size', parseInt(e.target.value))}
                min="100"
                max="2000"
                style={styles.input}
              />
            </div>
          </>
        )}

        {/* Semantic Settings */}
        {config.chunking_strategy === 'semantic' && (
          <div style={styles.field}>
            <label style={styles.label}>Similarity Threshold:</label>
            <input
              type="number"
              value={config.semantic_threshold}
              onChange={(e) => handleChange('semantic_threshold', parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              style={styles.input}
            />
          </div>
        )}

        {/* Embedding Provider */}
        <div style={styles.field}>
          <label style={styles.label}>Embedding Provider:</label>
          <select
            value={config.embedding_provider}
            onChange={(e) => handleChange('embedding_provider', e.target.value)}
            style={styles.select}
          >
            <option value="openai">OpenAI</option>
            <option value="cohere">Cohere</option>
            <option value="google">Google</option>
            <option value="fastembed">FastEmbed (Local)</option>
          </select>
        </div>

        {/* Embedding Model */}
        <div style={styles.field}>
          <label style={styles.label}>Embedding Model:</label>
          <input
            type="text"
            value={config.embedding_model}
            onChange={(e) => handleChange('embedding_model', e.target.value)}
            style={styles.input}
            placeholder="e.g., text-embedding-3-small"
          />
        </div>

        {/* Embedding Dimension */}
        <div style={styles.field}>
          <label style={styles.label}>Embedding Dimension:</label>
          <input
            type="number"
            value={config.embedding_dimension}
            onChange={(e) => handleChange('embedding_dimension', parseInt(e.target.value))}
            min="384"
            max="3072"
            style={styles.input}
          />
        </div>

        {/* Collection Name */}
        <div style={styles.field}>
          <label style={styles.label}>Collection Name:</label>
          <input
            type="text"
            value={config.collection_name || ''}
            onChange={(e) => handleChange('collection_name', e.target.value)}
            style={styles.input}
            placeholder="documents"
          />
        </div>
      </div>
    </div>
  );
};

const styles = {
  section: {
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: '20px',
    color: '#555',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '15px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
  },
  label: {
    marginBottom: '5px',
    fontWeight: 'bold',
    color: '#333',
    fontSize: '14px',
  },
  input: {
    padding: '8px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
  },
  select: {
    padding: '8px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: 'white',
  },
};

export default ConfigPanel;
