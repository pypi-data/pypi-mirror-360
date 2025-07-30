import click
from moviecli.ytswebs import *
from moviecli.utils import *
from InquirerPy import inquirer
from moviecli.torrent_downloader import TorrentDownloader
import threading
import time

@click.command()
@click.argument('movie')
def search(movie):
    results = search_movie(movie)
    choices, dict = format_search_results_into_choices(results)

    selection = inquirer.select(
        message="Select a movie:",
        default=choices[0],
        choices=choices,
        pointer='=>',
        instruction='Use arrow keys to navigate and Enter to select.',
    ).execute()

    click.secho(f'You selected {selection}', fg="green")

    url = dict[selection]
    movie_details = get_movie_details(url)
    details, options, dict = format_movie_details(movie_details)

    click.secho(details, fg="blue")
    selection = inquirer.select(
        message="Select a download option:",
        default=options[0],
        choices=options,
        pointer='=>',
        instruction='Use arrow keys to navigate and Enter to select.',
    ).execute()

    torrent_url = dict[selection]
    filename = download_torrent(torrent_url)

    downloader = TorrentDownloader(file_path=filename, save_path='.')

    def start_download_thread():
        downloader.start_download()

    download_thread = threading.Thread(target=start_download_thread)
    download_thread.start()

    while downloader.status in ["downloading", "paused"]:
        print(f"\rProgress: {downloader.get_progress()}%", end="")

        action = inquirer.select(
            message="\nChoose an action:",
            choices=["Pause", "Resume", "Stop", "Refresh"],
        ).execute()

        if action == "Pause":
            downloader.pause_download()
        elif action == "Resume":
            downloader.resume_download()
        elif action == "Stop":
            downloader.stop_download()
            break
        elif action == "Refresh":
            continue

        time.sleep(1)

    click.secho("\nDownload ended!", fg="yellow")

if __name__=='__main__':
    search()