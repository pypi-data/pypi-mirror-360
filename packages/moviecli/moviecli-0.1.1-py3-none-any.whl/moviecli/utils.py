def format_search_results_into_choices(search_results):
    choices = []
    dict = {}
    for i, result in enumerate(search_results, start=1):
        title = result[0]
        url = result[1]
        year = result[3]
        choice = f'{i}. {title} ({year})'
        choices.append(choice)
        dict[choice] = url
    return choices, dict

def format_movie_details(movie_details):
    title = movie_details[0]
    year = movie_details[1]
    categories = movie_details[2]
    tomatometer = movie_details[3]
    audience = movie_details[4]
    imdb = movie_details[5]

    dict = movie_details[6]
    choices = []
    for key in dict.keys():
        choices.append(key)

    details = f'''
Title: {title}
Year: {year}
Categories: {categories}
Tomatometer: {tomatometer}
Audience: {audience}
IMDb: {imdb}
'''
    del choices[-1]
    return details, choices, dict
