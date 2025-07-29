from golpo import Golpo

golpo_client = Golpo(api_key='De3NbKrjvw8cOygsgrPLg2lpZfAQ1o265heLJE3V')

podcast_url = golpo_client.create_podcast(
    prompt="Summarize",
    add_music=True, 
    style='solo-female', 
    bg_music="jazz", 
    bg_volume=2.0, 
    uploads=['/Users/shreyas/Downloads/summarize.txt']

)
print(podcast_url)

print(f"Podcast URL: {podcast_url}")
