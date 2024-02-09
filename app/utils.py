import re

import aiohttp
from bs4 import BeautifulSoup
import tiktoken


async def extract_and_clean_links(text):
    pattern = r'\b(?:https?://)?(?:www\.)?(\S+\.\S+)'
    raw_links = re.findall(pattern, text)

    cleaned_links = []
    for link in raw_links:
        cleaned_link = re.sub(r'[.,/]+$', '', link)
        if not cleaned_link.startswith(('http://', 'https://')):
            cleaned_link = 'https://' + cleaned_link
        print(cleaned_link)
        if await is_webpage_async(cleaned_link):
            cleaned_links.append(cleaned_link)

    return cleaned_links


async def is_webpage_async(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content_type = response.headers.get('content-type', '').lower()
                return content_type.startswith('text/html')
    except Exception as e:
        print(f"Error while checking the URL: {str(e)}")
        return False


async def url_text(session, msg):
    try:
        if msg[0] != "h":
            msg = msg[1:-1]

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
        }
        async with session.get(msg, headers=headers) as response:
            html = await response.read()

        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        print(f"Failed to open link: {str(e)}")
        return None


async def count_cut_tokens(sentence, token_limit):
    enc = tiktoken.get_encoding("cl100k_base")
    while len(enc.encode(sentence)) > token_limit:
        sentence = sentence[:-100]
    print(len(enc.encode(sentence)))
    print(len(sentence))
    return sentence
