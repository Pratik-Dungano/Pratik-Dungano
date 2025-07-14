import requests
from collections import defaultdict

USERNAME = "Pratik-Dungano"
BASE_URL = f"https://api.github.com/users/{USERNAME}/repos"
HEADERS = {"Accept": "application/vnd.github+json"}

# Framework and devicon mapping
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
        if not data: break
        repos.extend(data)
        page += 1
    return repos

def analyze(repos):
    lang_count = defaultdict(int)
    frameworks = set()

    for repo in repos:
        # Languages
        lang_url = repo["languages_url"]
        lang_data = requests.get(lang_url, headers=HEADERS).json()
        for lang, bytes_used in lang_data.items():
            lang_count[lang] += bytes_used

        # Framework detection from description or name
        description = (repo.get("description") or "") + repo.get("name", "")
        for keyword, icon in framework_keywords.items():
            if keyword.lower() in description.lower():
                frameworks.add(icon)

    top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:8]
    return top_langs, sorted(frameworks)

def generate_md(langs, frameworks):
    md = "## 🛠️ Top Skills Based on GitHub Repos\n\n<p align='left'>\n"
    for lang, _ in langs:
        icon = lang_icon_map.get(lang)
        if icon:
            md += f"  <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{icon}/{icon}-original.svg' alt='{lang}' width='40' height='40'/>\n"

    for fw in frameworks:
        md += f"  <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{fw}/{fw}-original.svg' alt='{fw}' width='40' height='40'/>\n"
    md += "</p>\n"
    return md

def update_readme(skills_md):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

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
    langs, frameworks = analyze(repos)
    md = generate_md(langs, frameworks)
    update_readme(md)
    print("README updated.")
