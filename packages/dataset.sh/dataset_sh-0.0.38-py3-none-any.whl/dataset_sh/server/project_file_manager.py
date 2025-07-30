import os
import datetime
from pydantic import BaseModel


class ArticleEntry(BaseModel):
    name: str
    mtime: str


class ProjectArticleManager:

    def __init__(self, base_folder):
        self.base_folder = os.path.normpath(base_folder)

    def list_articles(self, scan_folder: str = None) -> list[ArticleEntry]:
        if scan_folder is None:
            scan_folder = self.base_folder
        articles = []

        cat_file = os.path.join(self.base_folder, '__items__.txt')

        if os.path.exists(cat_file):
            with open(cat_file) as fd:
                for line in fd:
                    line = line.strip()
                    if line:
                        file_name = f"{line}.md"
                        file_path = os.path.join(self.base_folder, file_name)
                        if os.path.exists(file_path):
                            mtime = os.path.getmtime(file_path)
                            mtime_iso = datetime.datetime.fromtimestamp(mtime).isoformat()
                            name = file_name[:-3]
                            articles.append(ArticleEntry(name=name, mtime=mtime_iso))
        else:
            for file_name in os.listdir(scan_folder):
                if file_name.endswith('.md'):
                    file_path = os.path.join(self.base_folder, file_name)
                    mtime = os.path.getmtime(file_path)
                    mtime_iso = datetime.datetime.fromtimestamp(mtime).isoformat()
                    name = file_name[:-3]
                    articles.append(ArticleEntry(name=name, mtime=mtime_iso))
            articles.sort(key=lambda x: x.mtime, reverse=True)

        return articles

    def extract_article(self, file_name):
        file_path = os.path.join(self.base_folder, f"{file_name}.md")
        file_path = os.path.normpath(file_path)
        if not file_path.startswith(self.base_folder):
            return None
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                full_content = file.read()
                return full_content
        else:
            return None

    def write_article(self, file_name, content):
        file_path = os.path.join(self.base_folder, f"{file_name}.md")
        file_path = os.path.normpath(file_path)
        if not file_path.startswith(self.base_folder):
            return None

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as out:
            out.write(content)
