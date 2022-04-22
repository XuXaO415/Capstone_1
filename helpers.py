def get_articles(data):
    
    articles = data['articles']
    
    stories = []
    
    for article in articles:
        story = {
            'id': article['idArticle']
        }