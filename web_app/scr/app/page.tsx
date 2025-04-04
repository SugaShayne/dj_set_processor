export default function HomePage() {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>DJ Set Processor</h1>
      
      <div style={{ padding: '20px', border: '1px solid #eaeaea', borderRadius: '8px' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Process your DJ sets for YouTube compatibility</h2>
        
        <p style={{ marginBottom: '1rem' }}>
          Welcome to the DJ Set Processor! This application helps you:
        </p>
        
        <ul style={{ marginLeft: '20px', marginBottom: '1rem' }}>
          <li>Generate tracklists from your DJ sets</li>
          <li>Check tracks for YouTube compatibility</li>
          <li>Edit videos to remove blocked content</li>
          <li>Create thumbnails for YouTube uploads</li>
        </ul>
        
        <div style={{ textAlign: 'center' }}>
          <button 
            style={{ 
              backgroundColor: '#0070f3', 
              color: 'white', 
              padding: '10px 20px', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Get Started
          </button>
        </div>
      </div>
      
      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#666' }}>
        <p>DJ Set Processor - A tool for DJs to prepare their mixes for YouTube</p>
      </div>
    </div>
  );
}
