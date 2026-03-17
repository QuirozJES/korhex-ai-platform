const fs = require('fs');

let content = fs.readFileSync('frontend/src/App.jsx', 'utf8');

// Colors replacement
content = content.replace(/bg-\\[#080f18\\]/g, 'bg-hpe-bg');
content = content.replace(/bg-\\[#0a1628\\]/g, 'bg-hpe-panel');
content = content.replace(/border-slate-[78]00(?:\/\d+)?/g, 'border-hpe-border');
content = content.replace(/emerald-400/g, 'hpe-green');
content = content.replace(/emerald-500/g, 'hpe-green');
content = content.replace(/emerald-600/g, 'hpe-green');
content = content.replace(/hover:bg-hpe-green/g, 'hover:bg-hpe-green-hover');

// Fix the sidebar background specifically
content = content.replace(/aside className="w-52 shrink-0 bg-hpe-panel/g, 'aside className="w-52 shrink-0 bg-hpe-sidebar');

fs.writeFileSync('frontend/src/App.jsx', content, 'utf8');
console.log('Colors replaced in App.jsx');
