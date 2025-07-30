const voittaLogoSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="5 5 50 50">
  <defs>
    <!-- Gradients -->
    <linearGradient id="logo-gradient-1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4A00E0" />
      <stop offset="100%" stop-color="#0084FF" />
    </linearGradient>
    <linearGradient id="logo-gradient-2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0084FF" />
      <stop offset="100%" stop-color="#00E0A3" />
    </linearGradient>
    
    <!-- Filters -->
    <filter id="logo-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="1" dy="1" stdDeviation="1.5" flood-opacity="0.3" />
    </filter>
    
    <!-- Patterns -->
    <pattern id="circuit-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 10 40 M 20 0 L 20 40 M 30 0 L 30 40 M 0 10 L 40 10 M 0 20 L 40 20 M 0 30 L 40 30" 
            stroke="#4A00E0" stroke-width="0.5" stroke-opacity="0.2" fill="none" />
    </pattern>
  </defs>
  
  <!-- Logo Mark -->
  <g transform="translate(30, 30)">
    <!-- Background Circuit Pattern -->
    <circle cx="0" cy="0" r="25" fill="url(#circuit-pattern)" opacity="0.1" />
    
    <!-- Outer Circle -->
    <circle cx="0" cy="0" r="20" fill="url(#logo-gradient-1)" filter="url(#logo-shadow)" />
    
    <!-- Inner Network Pattern -->
    <g>
      <!-- Central Node -->
      <circle cx="0" cy="0" r="6" fill="#FFFFFF" opacity="0.9" />
      
      <!-- Connection Lines -->
      <path d="M 0 0 L -8 -8 M 0 0 L 8 -8 M 0 0 L -8 8 M 0 0 L 8 8" 
            stroke="white" stroke-width="2" stroke-linecap="round" />
      
      <!-- Outer Nodes -->
      <circle cx="-8" cy="-8" r="3" fill="white" />
      <circle cx="8" cy="-8" r="3" fill="white" />
      <circle cx="-8" cy="8" r="3" fill="white" />
      <circle cx="8" cy="8" r="3" fill="white" />
      
      <!-- Animated Data Flow -->
      <circle cx="0" cy="0" r="1" fill="#00E0A3">
        <animate attributeName="cx" values="0;-8" dur="1.5s" repeatCount="indefinite" />
        <animate attributeName="cy" values="0;-8" dur="1.5s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" repeatCount="indefinite" />
      </circle>
      
      <circle cx="0" cy="0" r="1" fill="#00E0A3">
        <animate attributeName="cx" values="0;8" dur="1.5s" begin="0.5s" repeatCount="indefinite" />
        <animate attributeName="cy" values="0;-8" dur="1.5s" begin="0.5s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.5s" repeatCount="indefinite" />
      </circle>
      
      <circle cx="0" cy="0" r="1" fill="#00E0A3">
        <animate attributeName="cx" values="0;-8" dur="1.5s" begin="1s" repeatCount="indefinite" />
        <animate attributeName="cy" values="0;8" dur="1.5s" begin="1s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="1s" repeatCount="indefinite" />
      </circle>
      
      <circle cx="0" cy="0" r="1" fill="#00E0A3">
        <animate attributeName="cx" values="0;8" dur="1.5s" begin="1.5s" repeatCount="indefinite" />
        <animate attributeName="cy" values="0;8" dur="1.5s" begin="1.5s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="1.5s" repeatCount="indefinite" />
      </circle>
    </g>
    
    <!-- Pulsing animation -->
    <circle cx="0" cy="0" r="20" fill="none" stroke="url(#logo-gradient-2)" stroke-width="1.5">
      <animate attributeName="r" values="20;23;20" dur="3s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="1;0.5;1" dur="3s" repeatCount="indefinite" />
    </circle>
    
    <!-- Rotating Outer Ring -->
    <g opacity="0.7">
      <circle cx="0" cy="-22" r="2" fill="#FFFFFF">
        <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite" />
      </circle>
      <circle cx="22" cy="0" r="2" fill="#FFFFFF">
        <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="90" to="450" dur="10s" repeatCount="indefinite" />
      </circle>
      <circle cx="0" cy="22" r="2" fill="#FFFFFF">
        <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="180" to="540" dur="10s" repeatCount="indefinite" />
      </circle>
      <circle cx="-22" cy="0" r="2" fill="#FFFFFF">
        <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="270" to="630" dur="10s" repeatCount="indefinite" />
      </circle>
    </g>
  </g>
</svg>`;

export function replaceJupyterLabLogo(): void {
  const logoElement = document.getElementById('jp-MainLogo');
  if (logoElement) {
    logoElement.innerHTML = voittaLogoSvg;
  }
}
