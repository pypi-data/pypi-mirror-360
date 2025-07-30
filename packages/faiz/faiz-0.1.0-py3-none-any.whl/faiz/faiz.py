import os
import sys
import subprocess
import glob
import requests
import webbrowser
# import utils.Rank as Rank
from .utils.env.env import main as env_main
from bs4 import BeautifulSoup
from .utils.edge.edge import edge_main_func, edgeMobileFun
from .utils.webpcon import convert_to_webp, process_images
from .utils.avif.avifcon import main as avif_main
from .utils.git import mainCall as git_main_or
from .utils.qr import main as qr
from .utils.cursor import move_cursor_randomly
from .utils.count.count import main as count_files_command


def main():
    if len(sys.argv) < 2:
        print("No subcommand provided.")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "avif": avif,
        "ssh": ssh_command,
        "reactjs": setup_reactjs,
        "laravel": setup_laravel,
        "search": google_search,
        "edge": edge_func,
        "edge_mobile": edgeMobileFunc,
        # "rank": rank_search,
        "webp": webp,
        "git": git_main,
        "qr": qr,
        "cursor": cursor,
        "count": count_files_command, 
        "env":get_command,
    }
    
    func = commands.get(command, invalid_command)
    func(args)


def cursor(args):
    move_cursor_randomly()

def get_command(args):
    env_main(args)
    

def git_main(args):
    git_main_or()


def avif(args):
    avif_main(args)

def webp(args):
    if len(sys.argv) < 3:
        print("Usage: python convert_to_webp.py <input_image_path_or_pattern> [output_image_path]")
    else:
        input_pattern = sys.argv[2]

        if "*" in input_pattern:
            image_files = glob.glob(input_pattern)
            if not image_files:
                print("❌ No matching files found.")
            else:
                print(f"🔄 Processing {len(image_files)} images in parallel...")
                process_images(image_files)
        else:
            input_path = input_pattern
            output_path = sys.argv[3] if len(sys.argv) > 3 else None
            convert_to_webp(input_path, output_path)


def edge_func(args):
    edge_main_func(30)
    return


def edgeMobileFunc(args):
    edgeMobileFun(20)
    return


def ssh_command(args):
    if len(args) < 1:
        print("Please enter your server name")
        return

    server = args[0]
    if server == "junoon":
        subprocess.run(["ssh", "-p", "65002", "u961915702@86.38.243.17"])
    elif server == "llm":
        subprocess.run(["ssh", "-i", "C:\\Users\\8FIN\\.ssh\\id_rsa", "faizrajput1519@34.28.155.233"])
    elif server == "shasha":
        subprocess.run([ "ssh", "-p", "65002", "u961915702@86.38.243.17"])
   
#    ssh -p 65002 u961915702@86.38.243.17
    else:
        print("Invalid server name")

def setup_reactjs(args):
    if len(args) < 1:
        print("You must specify a project name")
        return

    project_name = args[0]
    github_repo = "https://github.com/zokasta/reactjs.git"

    print("Cloning repository...")
    subprocess.run(["git", "clone", github_repo, project_name])

    os.chdir(project_name)

    print("Removing .git directory...")
    subprocess.run(["rm", "-rf", ".git"])

    print("Installing dependencies...")
    subprocess.run(["npm", "install"])
    subprocess.run(["npm", "update"])

    print(
        f"Project setup complete. Navigate to the {project_name} directory and start developing!"
    )

def setup_laravel(args):
    if len(args) < 1:
        print("You must specify a project name")
        return

    project_name = args[0]
    github_repo = "https://github.com/zokasta/laravel.git"

    print("Cloning repository...")
    subprocess.run(["git", "clone", github_repo, project_name])

    os.chdir(project_name)

    print("Removing .git directory...")
    subprocess.run(["rm", "-rf", ".git"])

    print("Installing dependencies...")
    subprocess.run(["composer", "install"])

    print("Copying .env.example to .env...")
    subprocess.run(["cp", ".env.example", ".env"])

    print("Generating application key...")
    subprocess.run(["php", "artisan", "key:generate"])

    print(
        f"Project setup complete. Navigate to the {project_name} directory and start developing!"
    )

def google_search(query):
    print('this feature is in alpha')
    if not query:
        print("You must provide a search query.")
        return

    print(f"Searching Google for: {query}")

    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    search_results = soup.find_all("a", href=True)

    for result in search_results:
        print(result)
        print('\n\n\n\n')
        link = result["href"]
        
        if link.startswith("https://"):
            link = link[7:].split("&")[0]
            print(f"First link: {link}")

            try:
                chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
                webbrowser.get(chrome_path).open(link)
                break  
            except webbrowser.Error:
                print("Error opening in Google Chrome. Opening in default browser...")
                webbrowser.open(link)
            break
    else:
        print("No valid results found.")

# def rank_search(args):
#     Rank.check_rank()

def invalid_command(args):
    print("Invalid subcommand.")


if __name__ == "__main__":
    main()


