from ytswebs import search_movie, get_movie_details

title, year, categories, tomatometer, audience, imdb, downloads = get_movie_details("https://yts.mx/movies/lego-marvel-super-heroes-avengers-reassembled-2015")

print(f'title:{title}\n')
print(f'year: {year}\n')
print(f'categories: {categories}\n')
print(f'tomatometer: {tomatometer}\n')
print(f'audience: {audience}\n')
print(f'imdb: {imdb}\n')
print('-------------')
for key in downloads.keys():
    print(f'=> {key}: {downloads[key]}')