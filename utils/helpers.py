def download_file(url, destination):
    import requests

    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as f:
            f.write(response.content)
        return True
    return False

def stream_data(data_generator):
    for data in data_generator:
        yield data

def format_link(text, url):
    return f'<a href="{url}" target="_blank">{text}</a>'