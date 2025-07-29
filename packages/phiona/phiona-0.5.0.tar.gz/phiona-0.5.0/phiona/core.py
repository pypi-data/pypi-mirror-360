import json
import librosa
import numpy as np
import requests


def calculate_features(song_path, sr=22050, chunk_size=256000):

    mono_data, sr = librosa.load(song_path, mono=True, sr=sr)
    # make sure the song is 22500 sr
    num_chunks = int(np.ceil(len(mono_data) / chunk_size))

    mel_chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(mono_data))
        if i > 0:
            chunk = mono_data[start-(2048-512):end]
        else:
            chunk = mono_data[start:end]
        if i == (num_chunks - 1):
            chunk = np.pad(chunk, (0, 512*2), 'constant')
        # Perform STFT
        if i == 0:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=True,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            mel_chunks.append(mel_result[:, :-2])
        else:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048, center=False)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=False,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            mel_chunks.append(mel_result)
    merged_mel_spec = np.hstack(mel_chunks)
    
    return merged_mel_spec


def upload_to_gbp(merged_mel_spec, npy_url):

    # Upload the NPY file to the signed URL
    headers = {'Content-Type': 'application/octet-stream'}
    response2 = requests.put(npy_url, data=merged_mel_spec.tobytes(), headers=headers)
    # Check if the upload was successful
    if response2.status_code == 200:
        print("npy file uploaded successfully to the signed URL.")


def process_song(access_token, song_path, song_title, artist_name, language, genre, date_released):
    response = requests.post(
        'http://localhost:8000/api/get_new_track_upload_urls',
        json={'song_title': song_title, 'artist_name': artist_name, 'language': language, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    data = json.loads(response.content)
    track_id = data['track_id']
    npy_url = data['npy_url']
    merged_mel_spec= calculate_features(song_path)
    upload_to_gbp(merged_mel_spec, npy_url)
    return track_id


def generate_predictions(access_token, track_id):
    response = requests.post(
        'http://localhost:8000/api/generate_emotions',
        json={'track_id': track_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    if response.status_code == 200:
        print('predictions generation success')


def get_file_status(access_token, sorting_mechanism=[]):
    response = requests.post(
        'http://localhost:8000/api/get_files',
        json={'sorting_mechanism': sorting_mechanism},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    song_info = json.loads(response.content)['song_info']
    
    return song_info


def generate_playlist_raw(access_token, targets, age_window=None, required_duration=1800):
    vars = {'targets': targets, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'http://localhost:8000/api/generate_user_playlist_raw',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_presets(access_token, preset, required_duration=1800):
    vars = {'targets': preset, 'required_duration': required_duration}
    response = requests.post(
        'http://localhost:8000/api/generate_user_playlist_presets',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_from_songs(access_token, song_ids, age_window=None, required_duration=1800):
    vars = {'song_ids': song_ids, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'http://localhost:8000/api/generate_user_playlist_songs',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_similar_songs(access_token, song_id):
    vars = {'song_id': song_id}
    response = requests.post(
        'http://localhost:8000/api/return_similar_songs',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_refresh_token(username, password):
    response = requests.post(
        'http://localhost:8000/api/token/',
        json={'username': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    refresh_token = json.loads(response.content)['refresh']
    
    return refresh_token


def get_new_access_token(refresh_token):
    response = requests.post(
        'http://localhost:8000/api/token/refresh/',
        json={'refresh': refresh_token},
        headers={'Content-Type': 'application/json'}
    )
    access_token = json.loads(response.content)['access']
    
    return access_token


def add_new_file(access_token, song_path, song_title, artist_name, language, genre, date_released):
    track_id = process_song(access_token, song_path, song_title, artist_name, language, genre, date_released)
    generate_predictions(access_token, track_id)


def edit_song(access_token, song_id, song_title, artist_name, genre, date_released):
    response = requests.post(
        'http://localhost:8000/api/edit_song',
        json={'song_id': song_id, 'song_title': song_title, 'artist_name': artist_name, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def edit_user_playlist(access_token, playlist_id, new_playlist_name):
    response = requests.post(
        'http://localhost:8000/api/edit_user_playlist',
        json={'playlist_id': playlist_id, 'playlist_name': new_playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_song(access_token, song_id):
    response = requests.post(
        'http://localhost:8000/api/delete_song',
        json={'song_id': song_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_user_playlist(access_token, playlist_id):
    response = requests.post(
        'http://localhost:8000/api/delete_user_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_generated_playlist(access_token, playlist_id):
    response = requests.post(
        'http://localhost:8000/api/delete_generated_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def create_new_playlist(access_token, playlist_name):
    response = requests.post(
        'http://localhost:8000/api/create_new_playlist',
        json={'playlist_name': playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def add_song_to_playlist(access_token, playlist_id, song_id):
    response = requests.post(
        'http://localhost:8000/api/add_song_to_playlist',
        json={'song_id': song_id, 'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def load_user_playlists(access_token):
    response = requests.post(
        'http://localhost:8000/api/load_user_playlists',
        json={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['playlists_info']


def load_generated_playlists(access_token):
    response = requests.post(
        'http://localhost:8000/api/load_generated_playlists',
        json={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['generated_playlists_info']



def load_user_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'http://localhost:8000/api/load_user_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']


def load_generated_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'http://localhost:8000/api/load_generated_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']
