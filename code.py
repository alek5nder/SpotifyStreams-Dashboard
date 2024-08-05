import requests
import pandas as pd


def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_data = auth_response.json()
    return auth_data['access_token']

def search_track(track_name, artist_name, token, retries=3, delay=5):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
            response.raise_for_status()  # Raise an error for bad responses
            json_data = response.json()
            try:
                first_result = json_data['tracks']['items'][0]
                track_id = first_result['id']
                return track_id
            except (KeyError, IndexError):
                return None
        except RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def get_track_details(track_id, token, retries=3, delay=5):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
            response.raise_for_status()  # Raise an error for bad responses
            json_data = response.json()
            image_url = json_data['album']['images'][0]['url']
            return image_url
        except RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

client_id = '31624ab80cfe4ad2a562caf20ca48529'
client_secret = 'a73c2750b7314c84a3a679c736f54dfb'

access_token = get_spotify_token(client_id, client_secret)

df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')

if 'track_name' in df_spotify.columns and 'artist(s)_name' in df_spotify.columns:
    for i, row in df_spotify.iterrows():
        track_id = search_track(row['track_name'], row['artist(s)_name'], access_token)
        if track_id:
            image_url = get_track_details(track_id, access_token)
            if image_url:
                df_spotify.at[i, 'image_url'] = image_url

    df_spotify.to_csv('updated_spotify-2023.csv', index=False)
else:
    print("Error: Required columns 'track_name' and/or 'artist(s)_name' are not in the CSV file.")
