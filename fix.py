import os
import re

files_to_dark = ["developer.html", "help.html", "privacy.html", "delete-account.html"]
base_path = "d:/Projects/invopocket/website/"

def fix_dark_mode():
    for fname in files_to_dark:
        path = os.path.join(base_path, fname)
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update CSS root slightly if needed, but doing targeted replacement is safer
        content = content.replace("background:var(--white);color:var(--black)", "background:var(--black);color:var(--white)")
        content = content.replace("color:var(--black)", "color:var(--white)")
        content = content.replace("color:var(--g600)", "color:var(--g300)")
        content = content.replace("color:var(--g500)", "color:var(--g400)")
        content = content.replace("border:1px solid var(--g200)", "border:1px solid rgba(255,255,255,0.1)")
        content = content.replace("border-color:var(--g300)", "border-color:rgba(255,255,255,0.2)")
        content = content.replace("background:var(--white)", "background:var(--black)")
        content = content.replace("background:var(--g900)", "background:rgba(255,255,255,0.1)")
        content = content.replace("border:3px solid var(--g200)", "border:3px solid rgba(255,255,255,0.1)")
        
        # In case we accidentally replaced the nav-dots span
        content = content.replace("nav-dots span{display:block;width:4px;height:4px;border-radius:50%;background:var(--black)}", "nav-dots span{display:block;width:4px;height:4px;border-radius:50%;background:var(--white)}")
        
        # Remove emojis
        content = re.sub(r'[\U00010000-\U0010ffff]', '', content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

def fix_index():
    path = os.path.join(base_path, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove emoji
    content = re.sub(r'[\U00010000-\U0010ffff]', '', content)
    
    # Check if mobile menu already exists
    if "mobileMenu" not in content:
        # Add CSS for mobile menu
        css_addition = """
.nav-dots{display:none;cursor:pointer;padding:8px;border:none;background:none;flex-direction:column;gap:4px;align-items:center;justify-content:center}
.nav-dots span{display:block;width:4px;height:4px;border-radius:50%;background:var(--white)}
.mobile-menu{display:none;position:fixed;top:64px;right:0;left:0;background:rgba(0,0,0,0.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.06);box-shadow:0 8px 32px rgba(0,0,0,0.4);padding:16px 24px;z-index:998;flex-direction:column;gap:4px}
.mobile-menu.open{display:flex}
.mobile-menu a{font-size:15px;font-weight:500;color:var(--g400);text-decoration:none;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.06);transition:color .15s}
.mobile-menu a:last-child{border-bottom:none}
.mobile-menu a:hover,.mobile-menu a.active{color:var(--white)}
"""
        # Replace the simple media query for nav with the advanced one
        old_media = "@media(max-width:768px){ nav { padding: 0 20px; } .nav-links { display: none; } }"
        new_media = """@media(max-width:768px){ 
  nav { padding: 0 20px; } 
  .nav-links { display: none; }
  .nav-dl { display: none; }
  .nav-dots { display: flex; }
}"""
        if old_media in content:
            content = content.replace(old_media, css_addition + "\n" + new_media)
        
        # Add the nav dots button before </nav>
        dots_html = """
  <button class="nav-dots" id="menuToggle" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</nav>"""
        content = content.replace("</nav>", dots_html, 1)

        # Add the mobile menu immediately after </nav>
        menu_html = """
<div class="mobile-menu" id="mobileMenu">
  <a href="#features">Features</a>
  <a href="#manage">Workflow</a>
  <a href="#download">Download</a>
  <a href="help.html">Help Center</a>
  <a href="privacy.html">Privacy</a>
  <a href="delete-account.html">Delete Account</a>
  <a href="developer.html">Developer</a>
</div>
"""
        content = content.replace("</nav>", "</nav>\n" + menu_html, 1)

        # Add the toggle script before </body>
        script_html = """
<script>
const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');
if(menuToggle && mobileMenu) {
  menuToggle.addEventListener('click', () => { mobileMenu.classList.toggle('open'); });
  document.addEventListener('click', (e) => {
    if (!mobileMenu.contains(e.target) && !menuToggle.contains(e.target)) mobileMenu.classList.remove('open');
  });
}
</script>
</body>"""
        content = content.replace("</body>", script_html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

fix_dark_mode()
fix_index()
print("Done!")
