function insertHeader() {
    document.getElementById('header-container').innerHTML = `
        <header>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1584 132" width="100%" height="132px">
                <!-- Clean white background -->
                <rect width="1584" height="132" fill="white" />
                
                <!-- ML algorithm trees inspired by XGBoost visualization but positioned like original header -->
                <g>
                    <!-- Left side XGBoost-inspired tree - vertical orientation spanning 2/3 height -->
                    <g>
                        <!-- Root node -->
                        <circle cx="170" cy="13" r="5" fill="#7E57C2" />
                        
                        <!-- Level 1 nodes -->
                        <circle cx="150" cy="27" r="4" fill="#5C6BC0" />
                        <circle cx="190" cy="27" r="4" fill="#5C6BC0" />
                        
                        <!-- Level 2 nodes -->
                        <circle cx="140" cy="40" r="3" fill="#42A5F5" />
                        <circle cx="160" cy="40" r="3" fill="#7E57C2" />
                        <circle cx="180" cy="40" r="3" fill="#42A5F5" />
                        <circle cx="200" cy="40" r="3" fill="#7E57C2" />
                        
                        <!-- Level 3 nodes -->
                        <circle cx="130" cy="53" r="3" fill="#7E57C2" />
                        <circle cx="150" cy="53" r="3" fill="#42A5F5" />
                        <circle cx="170" cy="53" r="3" fill="#7E57C2" />
                        <circle cx="190" cy="53" r="3" fill="#42A5F5" />
                        
                        <!-- Level 4 nodes -->
                        <circle cx="125" cy="67" r="2" fill="#42A5F5" />
                        <circle cx="135" cy="67" r="2" fill="#7E57C2" />
                        <circle cx="145" cy="67" r="2" fill="#42A5F5" />
                        <circle cx="155" cy="67" r="2" fill="#7E57C2" />
                        <circle cx="165" cy="67" r="2" fill="#42A5F5" />
                        <circle cx="175" cy="67" r="2" fill="#7E57C2" />
                        <circle cx="185" cy="67" r="2" fill="#42A5F5" />
                        <circle cx="195" cy="67" r="2" fill="#7E57C2" />
                        
                        <!-- Tree connections -->
                        <path d="M170 18 L150 23" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M170 18 L190 23" stroke="#333333" stroke-width="0.8" fill="none" />
                        
                        <path d="M150 31 L140 37" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M150 31 L160 37" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M190 31 L180 37" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M190 31 L200 37" stroke="#333333" stroke-width="0.8" fill="none" />
                        
                        <path d="M140 43 L130 50" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M140 43 L150 50" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M160 43 L170 50" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M180 43 L190 50" stroke="#333333" stroke-width="0.8" fill="none" />
                        
                        <path d="M130 56 L125 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M130 56 L135 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M150 56 L145 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M150 56 L155 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M170 56 L165 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M170 56 L175 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M190 56 L185 64" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M190 56 L195 64" stroke="#333333" stroke-width="0.8" fill="none" />
                    </g>
                    
                    <!-- Right side XGBoost-inspired tree - horizontal orientation at top -->
                    <g>
                        <!-- First level -->
                        <circle cx="875" cy="13" r="4" fill="#5C6BC0" />
                        <circle cx="995" cy="13" r="4" fill="#5C6BC0" />
                        
                        <!-- Second level -->
                        <circle cx="845" cy="13" r="3" fill="#42A5F5" />
                        <circle cx="905" cy="13" r="3" fill="#7E57C2" />
                        <circle cx="965" cy="13" r="3" fill="#42A5F5" />
                        <circle cx="1025" cy="13" r="3" fill="#7E57C2" />
                        
                        <!-- Third level -->
                        <circle cx="830" cy="20" r="3" fill="#7E57C2" />
                        <circle cx="860" cy="20" r="3" fill="#42A5F5" />
                        <circle cx="890" cy="20" r="3" fill="#7E57C2" />
                        <circle cx="920" cy="20" r="3" fill="#42A5F5" />
                        <circle cx="950" cy="20" r="3" fill="#7E57C2" />
                        <circle cx="980" cy="20" r="3" fill="#42A5F5" />
                        <circle cx="1010" cy="20" r="3" fill="#7E57C2" />
                        <circle cx="1040" cy="20" r="3" fill="#42A5F5" />
                        
                        <!-- Fourth level -->
                        <circle cx="820" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="840" cy="27" r="2" fill="#7E57C2" />
                        <circle cx="860" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="880" cy="27" r="2" fill="#7E57C2" />
                        <circle cx="900" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="920" cy="27" r="2" fill="#7E57C2" />
                        <circle cx="940" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="960" cy="27" r="2" fill="#7E57C2" />
                        <circle cx="980" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="1000" cy="27" r="2" fill="#7E57C2" />
                        <circle cx="1020" cy="27" r="2" fill="#42A5F5" />
                        <circle cx="1040" cy="27" r="2" fill="#7E57C2" />
                        
                        <!-- Connections - horizontal tree - updated to connect across without root -->
                        <path d="M875 13 L995 13" stroke="#333333" stroke-width="0.8" fill="none" />
                        
                        <path d="M845 13 L830 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M845 13 L860 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M905 13 L890 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M905 13 L920 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M965 13 L950 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M965 13 L980 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M1025 13 L1010 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M1025 13 L1040 19" stroke="#333333" stroke-width="0.8" fill="none" />
                        
                        <path d="M830 22 L820 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M830 22 L840 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M860 22 L860 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M860 22 L880 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M890 22 L900 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M920 22 L920 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M950 22 L940 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M980 22 L960 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M980 22 L980 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M1010 22 L1000 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M1010 22 L1020 25" stroke="#333333" stroke-width="0.8" fill="none" />
                        <path d="M1040 22 L1040 25" stroke="#333333" stroke-width="0.8" fill="none" />
                    </g>
                </g>
                
                <!-- Name text - modern artistic serif font (similar to example) -->
                <text x="280" y="40" font-family="'Didot', 'Bodoni MT', 'Playfair Display', serif" font-size="45" font-weight="400" fill="#000000">Mark Attwood</text>
                
                <!-- Job title -->
                <text x="670" y="55" font-family="'Libre Baskerville', 'Georgia', serif" font-size="20" font-weight="400" fill="#1A1A1A">Data Science &amp; Analytics</text>
                
                <!-- Email with globe icon - moved up to accommodate banner -->
                <g>
                    <circle cx="400" y="80" r="10" fill="none" stroke="#333333" stroke-width="1.5" />
                    <path d="M400 70 v20 M390 80 h20 M395 75 a10 10 0 0 0 0 10 M405 75 a10 10 0 0 1 0 10" fill="none" stroke="#333333" stroke-width="1.5" />
                    <text x="430" y="84" font-family="'Libre Baskerville', 'Georgia', serif" font-size="16" font-weight="400" fill="#1A1A1A">attwoodanalytics@gmail.com</text>
                </g>
                
                <!-- Bottom bar with gradient - color scheme more like example -->
                <rect x="43" y="95" width="1500" height="28" fill="url(#skillsGradient)" />
                
                <!-- Skills text - stylized serif font -->
                <text x="792" y="115" font-family="'Didot', 'Bodoni MT', 'Libre Baskerville', serif" font-size="18" font-weight="400" letter-spacing="2" fill="white" text-anchor="middle">
                    SQL | PYTHON | BI | AI | MACHINE LEARNING
                </text>
                
                <!-- Gradient definitions -->
                <defs>
                    <linearGradient id="skillsGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#7E57C2" stop-opacity="0.8" />
                        <stop offset="50%" stop-color="#5C6BC0" stop-opacity="0.8" />
                        <stop offset="100%" stop-color="#42A5F5" stop-opacity="0.8" />
                    </linearGradient>
                </defs>
            </svg>
            <div class="nav-container">
                <a href="index.html" class="home-button">Home</a>
            </div>
        </header>
    `;
}

// Add CSS for the home button
function addHomeButtonStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .nav-container {
            background-color: white;
            padding: 8px 0;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .home-button {
            display: inline-block;
            background-color: #7E57C2;
            color: white;
            text-decoration: none;
            padding: 0.5rem 1.2rem;
            border-radius: 4px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            transition: background-color 0.2s ease;
        }
        .home-button:hover {
            background-color: #6A48B0;
        }
    `;
    document.head.appendChild(style);
}

// Initialize the header when the DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById('header-container')) {
        addHomeButtonStyles();
        insertHeader();
    }
});
