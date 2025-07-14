import requests
from collections import defaultdict

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
    "JavaScript": "javascript",
    "Python": "python",
    "HTML": "html5",
    "CSS": "css3",
    "C++": "cplusplus",
    "C": "c",
    "TypeScript": "typescript",
    "Java": "java",
    "Shell": "bash",
    "Go": "go",
    "PHP": "php",
    "Ruby": "ruby",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Rust": "rust",
    "Dart": "dart"
}

def get_all_repos():
    repos, page = [], 1
    while True:
        res = requests.get(BASE_URL + f"?page={page}&per_page=100", headers=HEADERS)
        data = res.json()
        if not data or "message" in data:
            break
        repos.extend(data)
        page += 1
    return repos

def analyze(repos):
    lang_count = defaultdict(int)
    all_langs = set()
    frameworks = set()

    for repo in repos:
        lang_data = requests.get(repo["languages_url"], headers=HEADERS).json()
        for lang, bytes_used in lang_data.items():
            lang_count[lang] += bytes_used
            all_langs.add(lang)

        text = f"{repo.get('description', '')} {repo.get('name', '')}".lower()
        for keyword, icon in framework_keywords.items():
            if keyword in text:
                frameworks.add(icon)

    top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:8]
    return top_langs, sorted(all_langs), sorted(frameworks)

def badge(icon):
    return f"<img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{icon}/{icon}-original.svg' width='40' height='40'/>"

def generate_md(top_langs, all_langs, frameworks):
    md = "## 🛠️ Top Skills Based on GitHub Repos\n\n<p align='left'>\n"
    for lang, _ in top_langs:
        if icon := lang_icon_map.get(lang):
            md += f"  {badge(icon)}\n"
    for fw in frameworks:
        md += f"  {badge(fw)}\n"
    md += "</p>\n\n"

    md += "## 📋 All Technologies Used\n\n<p align='left'>\n"
    for lang in all_langs:
        if icon := lang_icon_map.get(lang):
            md += f"  {badge(icon)}\n"
    for fw in frameworks:
        md += f"  {badge(fw)}\n"
    md += "</p>\n"

    return md

def update_readme(skills_md):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = "# 👋 Welcome to My Profile\n\n"

    start_tag = "## 🛠️ Top Skills Based on GitHub Repos"
    if start_tag in content:
        pre = content.split(start_tag)[0].strip()
    else:
        pre = content.strip()
    new_content = f"{pre}\n\n{skills_md}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    repos = get_all_repos()
    if not repos:
        raise Exception("Could not fetch repositories. Possibly hit GitHub rate limit.")
    top_langs, all_langs, frameworks = analyze(repos)
    md = generate_md(top_langs, all_langs, frameworks)
    update_readme(md)
    print("README.md updated successfully.")
