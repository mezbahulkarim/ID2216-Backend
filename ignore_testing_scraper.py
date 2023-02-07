from scrapers import *

#print(search_movie("   Rush        Hour     ")[0])
#print(search_game("      Metro    Exodus" )[0])
print(detail_game("https://store.steampowered.com/app/692890/Roboquest/?snr=1_7_7_151_150_1"))
#print(type(detail_game("https://store.steampowered.com/app/412020/Metro_Exodus/")['genres']))
#print(detail_movie('https://www.themoviedb.org/movie/77'))
#print(detail_movie('https://www.themoviedb.org/movie/219')['actors'])

#print(search_book("      The    Art of     War")[0])
#print(detail_book('https://www.goodreads.com//book/show/61439040-1984?from_search=true&from_srp=true&qid=9aYrPGLjgk&rank=1'))

#TESTING STUFF
# @app.get('/get_article')
# async def get_article():
    
#     searched: Book_Detail = detail_book('https://www.goodreads.com//book/show/61439040-1984?from_search=true&from_srp=true&qid=9aYrPGLjgk&rank=1')
#     return searched

#     # searched: Movie_Detail = detail_movie('https://www.themoviedb.org/movie/77')
#     # return searched


# @app.get('/getallbooks')    #works
# async def get_all_books():

#     books=db.query(models.Books).all()
#     return books

# @app.get('/insertbook')     #works
# async def insert_book():

#     record = models.Books(
    #     id = "Ok Testing",
    #     title = "Testing Insert",
    #     genres = [
    # "Classics",
    # "Fiction",
    # "Science Fiction",
    # "Dystopia",
    # "Literature",
    # "Novels"
    # ]
#     )

#     db.add(record)
#     db.commit()


#     return "Done"

# @app.get('/insertmovie')
# async def insert_movie():
    
#     acts =  [{'real_name': 'Guy Pearce', 'movie_name': 'Leonard Shelby', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/vTqk6Nh3WgqPubkS23eOlMAwmwa.jpg'}, {'real_name': 'Carrie-Anne Moss', 'movie_name': 'Natalie', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/xD4jTA3KmVp5Rq3aHcymL9DUGjD.jpg'}, {'real_name': 'Joe Pantoliano', 'movie_name': 'John Edward "Teddy" Gammell', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/cXMOad9KKVBK1lg8EjEbcNPn1OT.jpg'}, {'real_name': 'Mark Boone Junior', 'movie_name': 'Burt', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/rcncVr356hpfKX9qOrKL3SJlEO7.jpg'}, {'real_name': 'Russ Fega', 'movie_name': 'Waiter', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/d0W7kq97Ul8Iz5LZIVNDKxSly8M.jpg'}, {'real_name': 'Jorja Fox', 'movie_name': 'Catherine Shelby', 'image_url': 'https://www.themoviedb.org/t/p/w138_and_h175_face/hCRdbNzZjkhYyVoZPmhYF5OqpaX.jpg'}]
#     acts =json.dumps(acts)

#     record = models.Movies(
#         id = "Test",
#         actors = acts
#     ) 
#     db.add(record)
#     db.commit()

# @app.get('/insertgame')
# async def insert_game():
#     gen =  ['Post-apocalyptic', 'FPS', 'Open World', 'Story Rich', 'Singleplayer', 'Atmospheric']

#     record = models.Games(genres = gen,
#                             link = 123)
#     db.add(record)
#     db.commit()
#     return "g"

#TESTING STUFF


#Databaseings
# from sqlalchemy import URL

#user=postgres password=[YOUR-PASSWORD] host=db.dtohwsymdfnwstwyburf.supabase.co port=5432 database=postgres

# url_object = URL.create(
#     "postgresql",
#     username="postgres",
#     password=passwd,
#     host="db.dtohwsymdfnwstwyburf.supabase.co",
#     database="postgres"
# )