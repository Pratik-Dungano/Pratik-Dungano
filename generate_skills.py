import requests
from collections import defaultdict
from datetime import datetime, timedelta

USERNAME = "Pratik-Dungano"
BASE_URL = f"https://api.github.com/users/{USERNAME}/repos"
HEADERS = {"Accept": "application/vnd.github+json"}

framework_keywords = {
    "react": "react",
    "node": "nodejs",
    "express": "express",
    "flask": "flask",
    "django": "django",
    "next": "nextjs",
    "firebase": "firebase",
    "tailwind": "tailwindcss"
}

lang_icon_map = {
    "JavaScript": "javascript", "Python": "python", "HTML": "html5",
    "CSS": "css3", "C++": "cplusplus", "C": "c", "TypeScript": "typescript",
    "Java": "java", "Shell": "bash", "Go": "go", "PHP": "php",
    "Ruby": "ruby", "Kotlin": "kotlin", "Swift": "swift", "Rust": "rust",
    "Dart": "dart"
}

def get_all_repos():
    repos, page = [], 1
    while True:
        res = requests.get(BASE_URL + f"?page={page}&per_page=100", headers=HEADERS)
        if res.status_code != 200:
            raise Exception(f"❌ GitHub API error: {res.status_code} - {res.json().get('message')}")
        data = res.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def analyze(repos):
    lang_count = defaultdict(int)
    all_langs = set()
    frameworks = set()

    for repo in repos:
        try:
            lang_data = requests.get(repo["languages_url"], headers=HEADERS).json()
            for lang, bytes_used in lang_data.items():
                lang_count[lang] += bytes_used
                all_langs.add(lang)

            text = f"{repo.get('description', '')} {repo.get('name', '')}".lower()
            for keyword, icon in framework_keywords.items():
                if keyword in text:
                    frameworks.add(icon)
        except Exception as e:
            print(f"⚠️ Skipping repo: {repo.get('name', 'unknown')} due to error: {str(e)}")

    top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:8]
    return top_langs, sorted(all_langs), sorted(frameworks)

def badge(icon, label):
    return f"<img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{icon}/{icon}-original.svg' title='{label}' width='40' height='40'/>"

def generate_md(weekly, alltime):
    md = "<!-- SKILLS-SECTION-START -->\n"
    
    # Weekly Skills Section
    top_langs, _, frameworks = weekly
    md += "## 📆 Weekly Skills Worked On\n\n<p align='left'>\n"
    for lang, _ in top_langs:
        if icon := lang_icon_map.get(lang):
            md += f"  {badge(icon, lang)}\n"
    for fw in frameworks:
        md += f"  {badge(fw, fw.capitalize())}\n"
    md += "</p>\n\n"

    # All Time Skills Section
    _, all_langs, frameworks_all = alltime
    md += "## 📚 All Tech Skills Learned (All Repos)\n\n<p align='left'>\n"
    for lang in all_langs:
        if icon := lang_icon_map.get(lang):
            md += f"  {badge(icon, lang)}\n"
    for fw in frameworks_all:
        md += f"  {badge(fw, fw.capitalize())}\n"
    md += "</p>\n"
    
    md += "<!-- SKILLS-SECTION-END -->"
    return md

def update_readme(skills_md):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise Exception("❌ README.md not found. Create one at the root of your repo.")

    pre, post = "", ""
    if "<!-- SKILLS-SECTION-START -->" in content and "<!-- SKILLS-SECTION-END -->" in content:
        pre = content.split("<!-- SKILLS-SECTION-START -->")[0].strip()
        post = content.split("<!-- SKILLS-SECTION-END -->")[1].strip()
    else:
        pre = content.strip()
        post = ""

    new_content = f"{pre}\n\n{skills_md}\n\n{post}".strip()
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

def filter_recent_repos(repos, days=7):
    recent = []
    threshold = datetime.utcnow() - timedelta(days=days)
    for repo in repos:
        updated = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        if updated > threshold:
            recent.append(repo)
    return recent

if __name__ == "__main__":
    try:
        repos = get_all_repos()
        if not repos:
            raise Exception("❌ No public repositories found.")
        
        recent_repos = filter_recent_repos(repos, days=7)
        weekly_data = analyze(recent_repos)
        alltime_data = analyze(repos)

        md = generate_md(weekly_data, alltime_data)
        update_readme(md)
        print("✅ README.md updated with weekly and all-time skills.")
    except Exception as e:
        print(str(e))
        exit(1)
