import pandas as pd

rating = pd.read_csv('Rating_Books.csv')
Book_Data = pd.read_csv('Books.csv')
merged = pd.merge(Book_Data, rating)
# merged
# merged = merged.astype({"Book-Rating": int, "ISBN": str, "User-ID": int})

# print(merged.dtypes)

user_rating = merged.pivot_table(index='User-ID', columns='Book-Title', values='Book-Rating')

user_rating = user_rating.dropna(thresh=15, axis=1).fillna(0)

Book_similarity = user_rating.corr(method='pearson')


def recommend_Book(Book_name, user_rating):
    if Book_name in Book_similarity:
        Book_score = Book_similarity[Book_name] * (user_rating - 2.5)
        Book_score = Book_score.sort_values(ascending=False)
        return Book_score

new_user = [("A Painted House", 5)]

similar_Books = pd.DataFrame()
for Book, rating in new_user:
    similar_Books = similar_Books.append(recommend_Book(Book, rating), ignore_index=True)

print(similar_Books.sum().sort_values(ascending=False))