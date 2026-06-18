import os
import re

base_path = "d:/Projects/invopocket/website/"
files_to_update = ["developer.html", "help.html", "privacy.html", "delete-account.html"]

# 1. Add Neon Icons to index.html
with open(os.path.join(base_path, 'index.html'), 'r', encoding='utf-8') as f:
    index_html = f.read()

neon_icons = [
    '<svg viewBox="0 0 24 24" width="24" height="24" stroke="#00ff88" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 5px #00ff88);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    '<svg viewBox="0 0 24 24" width="24" height="24" stroke="#00f0ff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 5px #00f0ff);"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>',
    '<svg viewBox="0 0 24 24" width="24" height="24" stroke="#b026ff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 5px #b026ff);"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>',
    '<svg viewBox="0 0 24 24" width="24" height="24" stroke="#ffaa00" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 5px #ffaa00);"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>'
]

# We need to replace empty <div class="enc-node-icon"></div> with <div class="enc-node-icon"> [SVG] </div>
# Find all occurrences
parts = index_html.split('<div class="enc-node-icon"></div>')
if len(parts) == 5:
    new_index_html = parts[0]
    for i in range(4):
        new_index_html += f'<div class="enc-node-icon">{neon_icons[i]}</div>' + parts[i+1]
    
    with open(os.path.join(base_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(new_index_html)
        print("Updated index.html with neon icons.")
else:
    print("Could not find the 4 empty enc-node-icon divs in index.html.")


# 2. Get the Nav HTML and CSS from index.html
# Nav HTML
nav_match = re.search(r'(<nav>.*?</nav>)', index_html, re.DOTALL)
menu_match = re.search(r'(<div class="mobile-menu" id="mobileMenu">.*?</div>)', index_html, re.DOTALL)

if nav_match and menu_match:
    nav_html = nav_match.group(1)
    menu_html = menu_match.group(1)
    
    # Adapt links for subpages (e.g. href="#features" -> href="index.html#features")
    nav_html_adapted = re.sub(r'href="#(.*?)"', r'href="index.html#\1"', nav_html)
    menu_html_adapted = re.sub(r'href="#(.*?)"', r'href="index.html#\1"', menu_html)

    # Get .nav-dl CSS from index.html
    nav_dl_css_match = re.search(r'(\.nav-dl.*?\{.*?\})', index_html, re.DOTALL)
    nav_dl_hover_match = re.search(r'(\.nav-dl:hover.*?\{.*?\})', index_html, re.DOTALL)
    nav_dl_after_match = re.search(r'(\.nav-dl::after.*?\{.*?\})', index_html, re.DOTALL)
    nav_dl_hover_after_match = re.search(r'(\.nav-dl:hover::after.*?\{.*?\})', index_html, re.DOTALL)
    
    extra_css = ""
    for m in [nav_dl_css_match, nav_dl_hover_match, nav_dl_after_match, nav_dl_hover_after_match]:
        if m: extra_css += "\n" + m.group(1)

    # Add .nav-brand CSS adaptations for subpages to ensure logo and title look exactly like index
    extra_css += """
.nav-brand { display: flex; align-items: center; gap: 10px; }
.nav-logo { width: 34px; height: 34px; border-radius: 9px; object-fit: contain; }
.nav-name { font-size: 16px; font-weight: 800; letter-spacing: -0.4px; }
.nav-name span { color: var(--g500); }
.nav-links a { font-size: 13px; font-weight: 500; color: var(--g400); transition: color 0.2s; }
.nav-links a:hover { color: var(--white); }
"""

    for fname in files_to_update:
        filepath = os.path.join(base_path, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace <nav>
        content = re.sub(r'<nav.*?</nav>', nav_html_adapted, content, flags=re.DOTALL)
        
        # Replace mobile menu if exists
        if '<div class="mobile-menu"' in content:
            content = re.sub(r'<div class="mobile-menu".*?</div>', menu_html_adapted, content, flags=re.DOTALL)
        else:
            # Insert right after nav
            content = content.replace('</nav>', '</nav>\n' + menu_html_adapted)
            
        # Inject CSS if .nav-dl doesn't exist
        if '.nav-dl' not in content:
            content = content.replace('</style>', extra_css + '\n</style>')
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("Updated nav across all subpages.")
else:
    print("Nav or mobile menu not found in index.html")
