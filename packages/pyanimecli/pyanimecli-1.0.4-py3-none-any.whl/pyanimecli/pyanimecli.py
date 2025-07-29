import sys
import argparse
import requests
import platform
import subprocess
import tempfile
import shutil
import os
import re
from urllib.parse import quote

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.spinner import Spinner
except ImportError:
    print("Error: The 'rich' library is required. Please install it using 'pip install rich'.")
    sys.exit(1)

console = Console()

BASE_URL = "https://yumaapi.vercel.app"
PROXY_URL = "https://gammam3u8proxy-fxsb.vercel.app/cors?url="

def proxy_url(url):
    if not url:
        return ""
    return f"{PROXY_URL}{url}"

def make_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    spinner = Spinner("dots", text=Text(f"Fetching data from {url}...", style="cyan"))
    with Live(spinner, console=console, transient=True, refresh_per_second=20):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]API Request Error:[/bold red] {e}")
            return None
        except ValueError:
            console.print("[bold red]API Error:[/bold red] Failed to decode JSON from response.")
            return None

def clean_description(description):
    if not description:
        return "No description available."
    cleaned = re.sub(r'(\r\n)?\r?\n?\[Written by MAL Rewrite\]', '', description, flags=re.IGNORECASE).strip()
    return cleaned

def check_executable(name):
    return shutil.which(name) is not None

def display_search_results(results, title="Search Results"):
    if not results or not results.get("results"):
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=f"[bold cyan]{title}[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=40)
    table.add_column("Title", style="bold white", min_width=20)
    table.add_column("Type", style="green", width=8)
    table.add_column("Sub", style="blue", width=5)
    table.add_column("Dub", style="red", width=5)
    table.add_column("Duration", style="yellow", width=10)

    for item in results["results"]:
        table.add_row(
            item.get("id", "N/A"),
            item.get("title", "N/A"),
            item.get("type", "N/A"),
            str(item.get("sub", "0")),
            str(item.get("dub", "0")),
            item.get("duration", "N/A")
        )

    console.print(table)
    console.print(f"Page [bold]{results.get('current_page', 1)}[/bold] of [bold]{results.get('total_pages', 1)}[/bold]. Use -p <page_number> to navigate.")

def display_anime_info(info):
    if not info:
        console.print("[bold red]Could not retrieve anime info.[/bold red]")
        return

    title = info.get("title", "No Title")
    description = clean_description(info.get("description"))
    
    info_text = Text()
    info_text.append(f"ID: ", style="bold magenta")
    info_text.append(f"{info.get('id', 'N/A')}\n")
    info_text.append(f"Type: ", style="bold magenta")
    info_text.append(f"{info.get('type', 'N/A')}\n")
    info_text.append(f"Total Episodes: ", style="bold magenta")
    info_text.append(f"{info.get('total_episodes', 'N/A')}\n")
    info_text.append(f"Sub Episodes: ", style="bold magenta")
    info_text.append(f"{info.get('sub', 'N/A')}\n")
    info_text.append(f"Dub Episodes: ", style="bold magenta")
    info_text.append(f"{info.get('dub', 'N/A')}\n")
    info_text.append(f"Status: ", style="bold magenta")
    info_text.append(f"{info.get('status', 'N/A')}\n")
    info_text.append(f"Genres: ", style="bold magenta")
    info_text.append(f"{', '.join(info.get('genres', ['N/A']))}\n")
    info_text.append(f"Image: ", style="bold magenta")
    info_text.append(proxy_url(info.get('image', '')), style="cyan underline")

    console.print(Panel(info_text, title=f"[bold green]{title}[/bold green]", border_style="green", expand=False))
    console.print(Panel(description, title="[bold]Description[/bold]", border_style="blue"))
    
    episodes = info.get("episodes", [])
    if episodes:
        episode_table = Table(title="[bold cyan]Episodes[/bold cyan]", show_header=True, header_style="bold magenta")
        episode_table.add_column("Ep #", style="dim")
        episode_table.add_column("Title", style="bold white")
        episode_table.add_column("Episode ID", style="dim")

        for ep in episodes:
            episode_table.add_row(
                str(ep.get("number", "N/A")),
                ep.get("title", "N/A"),
                ep.get("id", "N/A")
            )
        console.print(episode_table)
        console.print("Use -w <Episode ID> <sub|dub> to watch.")

def display_spotlight(spotlight_data):
    if not spotlight_data:
        console.print("[yellow]No spotlight data found.[/yellow]")
        return
    
    console.print("[bold yellow]🌟 Spotlight 🌟[/bold yellow]")
    for item in spotlight_data:
        rank = item.get("other_data", {}).get("rank", "")
        title = item.get("title", "N/A")
        description = clean_description(item.get("other_data", {}).get("description", ""))
        release_date = item.get("other_data", {}).get("releaseDate", "N/A")

        panel_content = Text()
        panel_content.append(f"ID: ", style="bold magenta")
        panel_content.append(f"{item.get('id', 'N/A')}\n")
        panel_content.append(f"Release Date: ", style="bold magenta")
        panel_content.append(f"{release_date}\n\n")
        panel_content.append(description)

        console.print(Panel(
            panel_content,
            title=f"[bold green]{rank}: {title}[/bold green]",
            border_style="green"
        ))

def display_schedule(schedule_data, date):
    if not schedule_data:
        console.print(f"[yellow]No schedule found for {date}.[/yellow]")
        return
    
    table = Table(title=f"[bold cyan]Airing Schedule for {date}[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Time (UTC)", style="yellow")
    table.add_column("Title", style="bold white")
    table.add_column("Airing Episode", style="green")
    table.add_column("ID", style="dim")

    for item in schedule_data:
        other_data = item.get("other_data", {})
        table.add_row(
            other_data.get("airingTime", "N/A"),
            item.get("title", "N/A"),
            other_data.get("airingEpisode", "N/A"),
            item.get("id", "N/A")
        )
    console.print(table)

def display_suggestions(suggestions_data):
    if not suggestions_data:
        console.print("[yellow]No suggestions found.[/yellow]")
        return

    table = Table(title="[bold cyan]Search Suggestions[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Title", style="bold white")
    table.add_column("Alias", style="dim")
    table.add_column("Release Date", style="green")
    table.add_column("ID", style="dim")
    
    for item in suggestions_data:
        other_data = item.get("other_data", {})
        table.add_row(
            item.get("title", "N/A"),
            other_data.get("alias", "N/A"),
            other_data.get("releaseDate", "N/A"),
            item.get("id", "N/A")
        )
    console.print(table)
    
def search_anime(query, page):
    endpoint = f"search/{quote(query)}"
    data = make_request(endpoint, params={"page": page, "max_results": 10})
    if data:
        display_search_results(data)

def get_anime_info(anime_id):
    endpoint = f"info/{anime_id}"
    data = make_request(endpoint)
    if data:
        display_anime_info(data)

def watch_episode(episode_id, watch_type):
    if not check_executable("vlc"):
        console.print("[bold red]VLC not found.[/bold red] Please install it from 'https://www.videolan.org/vlc' and ensure it's in your system's PATH.")
        return

    is_windows = platform.system() == "Windows"
    downloader = "curl" if is_windows else "wget"

    if not check_executable(downloader):
        console.print(f"[bold red]{downloader.capitalize()} not found.[/bold red] Please install it and ensure it's in your system's PATH.")
        return

    endpoint = "watch"
    params = {"episodeId": episode_id, "type": watch_type}
    data = make_request(endpoint, params=params)

    if not data or not data.get("sources"):
        console.print("[bold red]Could not retrieve stream sources.[/bold red]")
        return

    stream_url = data["sources"][0].get("url")
    referrer = data["headers"].get("Referer")
    
    if not stream_url or not referrer:
        console.print("[bold red]Incomplete stream data received.[/bold red]")
        return
    
    proxied_stream_url = proxy_url(stream_url)
    vlc_command = ["vlc", proxied_stream_url, f"--http-referrer={referrer}"]
    
    sub_file_path = None
    if watch_type == "sub" and data.get("subtitles"):
        sub_url = data["subtitles"][0].get("url")
        if sub_url:
            proxied_sub_url = proxy_url(sub_url)
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".vtt") as tmp_file:
                sub_file_path = tmp_file.name

            console.print(f"Downloading subtitles to [cyan]{sub_file_path}[/cyan]...")
            
            if is_windows:
                download_cmd = ["curl", "-s", "-L", "-o", sub_file_path, proxied_sub_url]
            else:
                download_cmd = ["wget", "-q", "-O", sub_file_path, proxied_sub_url]
            
            try:
                subprocess.run(download_cmd, check=True)
                vlc_command.append(f"--sub-file={sub_file_path}")
                console.print("[green]Subtitle download complete.[/green]")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                console.print(f"[bold red]Failed to download subtitles:[/bold red] {e}")
                sub_file_path = None
    
    command_str = ' '.join(f'"{c}"' if ' ' in c else c for c in vlc_command)
    console.print(f"\n[bold]Executing command:[/bold]\n[yellow]{command_str}[/yellow]\n")

    try:
        subprocess.run(vlc_command)
    except Exception as e:
        console.print(f"[bold red]Failed to launch VLC:[/bold red] {e}")
    finally:
        if sub_file_path and os.path.exists(sub_file_path):
            os.remove(sub_file_path)

def get_recent_episodes(page):
    data = make_request("recent-episodes", params={"page": page})
    if data:
        display_search_results(data, title="Recently Updated Episodes")

def get_top_airing(page):
    data = make_request("top-airing", params={"page": page})
    if data:
        display_search_results(data, title="Top Airing Anime")

def list_genres():
    data = make_request("genre/list")
    if data:
        console.print(Panel(", ".join(data), title="[bold cyan]Available Genres[/bold cyan]", border_style="cyan"))

def search_by_genre(genre, page):
    endpoint = f"genre/{quote(genre)}"
    data = make_request(endpoint, params={"page": page})
    if data:
        display_search_results(data, title=f"Results for Genre: {genre.capitalize()}")

def search_by_studio(studio_id, page):
    endpoint = f"studio/{quote(studio_id)}"
    data = make_request(endpoint, params={"page": page})
    if data:
        display_search_results(data, title=f"Results for Studio: {studio_id}")

def get_schedule(date):
    endpoint = f"schedule/{date}"
    data = make_request(endpoint)
    if data is not None:
        display_schedule(data, date)

def get_spotlight():
    data = make_request("spotlight")
    if data:
        display_spotlight(data)

def get_search_suggestions(query):
    endpoint = f"search-suggestions/{quote(query)}"
    data = make_request(endpoint)
    if data:
        display_suggestions(data)

def display_help(command=None):
    console.print(Panel("[bold yellow]pyanimecli - A CLI for Watching Anime[/bold yellow]", expand=False, border_style="yellow"))
    
    help_data = {
        "search": ("-s, -search <query>", "Search for an anime."),
        "info": ("-i, -info <id>", "Get detailed information about an anime by its ID."),
        "watch": ("-w, -watch <episode_id> <sub|dub>", "Watch an episode using VLC. Requires episode ID and type (sub or dub)."),
        "recent": ("-re, -recent-episodes", "List recently updated episodes."),
        "top_airing": ("-ta, -top-airing", "List top airing anime."),
        "genres": ("-g, -genres", "List all available genres."),
        "genre_search": ("-gs, -genre-search <genre>", "Search for anime by a specific genre."),
        "studio": ("-st, -studio <studio_id>", "Search for anime by a studio ID."),
        "schedule": ("-sc, -schedule <YYYY-MM-DD>", "Get the airing schedule for a specific date."),
        "spotlight": ("-sp, -spotlight", "Show spotlight anime."),
        "suggestions": ("-ss, -search-suggestions <query>", "Get search suggestions for a query."),
        "pagination": ("-p, -page <number>", "Used with commands that support pages (search, recent, etc.).")
    }

    if command and command in help_data:
        usage, desc = help_data[command]
        console.print(f"\n[bold]Help for '{command}':[/bold]")
        console.print(f"  [cyan]Usage:[/cyan] {usage}")
        console.print(f"  [cyan]Description:[/cyan] {desc}")
    else:
        table = Table(title="[bold]Available Commands[/bold]", show_header=False, box=None)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description")
        for key, (usage, desc) in help_data.items():
            table.add_row(usage, desc)
        console.print(table)
        console.print("\nUse -h <command_name> (e.g., -h search) for specific command help.")

def main():
    parser = argparse.ArgumentParser(description="A command-line tool to interact with the YumaAPI for anime.", add_help=False)
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '-search', dest='search', nargs='+', help='Search for an anime.')
    group.add_argument('-i', '-info', dest='info', help='Get info for an anime by ID.')
    group.add_argument('-w', '-watch', dest='watch', nargs=2, metavar=('EPISODE_ID', 'TYPE'), help='Watch an episode (sub/dub).')
    group.add_argument('-re', '-recent-episodes', dest='recent', action='store_true', help='Get recent episodes.')
    group.add_argument('-ta', '-top-airing', dest='top_airing', action='store_true', help='Get top airing anime.')
    group.add_argument('-g', '-genres', dest='genres', action='store_true', help='List all genres.')
    group.add_argument('-gs', '-genre-search', dest='genre_search', nargs='+', help='Search by genre.')
    group.add_argument('-st', '-studio', dest='studio', nargs='+', help='Search by studio.')
    group.add_argument('-sc', '-schedule', dest='schedule', help='Get schedule for a date (YYYY-MM-DD).')
    group.add_argument('-sp', '-spotlight', dest='spotlight', action='store_true', help='Get spotlight anime.')
    group.add_argument('-ss', '-search-suggestions', dest='suggestions', nargs='+', help='Get search suggestions.')
    group.add_argument('-h', '-help', dest='help', nargs='?', const='all', help='Show this help message or help for a specific command.')

    parser.add_argument('-p', '-page', dest='page', type=int, default=1, help='Page number for paginated results.')

    if len(sys.argv) == 1:
        display_help()
        sys.exit(0)

    try:
        args = parser.parse_args()
        
        if args.help:
            cmd_map = {
                "search": "search", "s": "search",
                "info": "info", "i": "info",
                "watch": "watch", "w": "watch",
                "recent": "recent", "re": "recent", "recent-episodes": "recent",
                "top": "top_airing", "ta": "top_airing", "top-airing": "top_airing",
                "genres": "genres", "g": "genres",
                "genre-search": "genre_search", "gs": "genre_search",
                "studio": "studio", "st": "studio",
                "schedule": "schedule", "sc": "schedule",
                "spotlight": "spotlight", "sp": "spotlight",
                "suggestions": "suggestions", "ss": "suggestions", "search-suggestions": "suggestions",
                "page": "pagination", "p": "pagination"
            }
            command_to_help = cmd_map.get(args.help) if args.help != 'all' else None
            display_help(command_to_help)
        elif args.search:
            search_anime(' '.join(args.search), args.page)
        elif args.info:
            get_anime_info(args.info)
        elif args.watch:
            watch_episode(args.watch[0], args.watch[1].lower())
        elif args.recent:
            get_recent_episodes(args.page)
        elif args.top_airing:
            get_top_airing(args.page)
        elif args.genres:
            list_genres()
        elif args.genre_search:
            search_by_genre(' '.join(args.genre_search), args.page)
        elif args.studio:
            search_by_studio(' '.join(args.studio), args.page)
        elif args.schedule:
            get_schedule(args.schedule)
        elif args.spotlight:
            get_spotlight()
        elif args.suggestions:
            get_search_suggestions(' '.join(args.suggestions))
        else:
             display_help()

    except argparse.ArgumentError as e:
        console.print(f"[bold red]Argument Error:[/bold red] {e}")
        display_help()
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
