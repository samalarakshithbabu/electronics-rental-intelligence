"""Test product recommender"""
from ml.recommendations import ProductRecommender
from database.connection import get_all_products

print('Testing Product Recommender...')
recommender = ProductRecommender()
products = get_all_products()
print(f'Products: {len(products)}')

result = recommender.train(products)
print(f'Training result: {result}')
print(f'Is trained: {recommender.is_trained}')

# Test similar products
similar = recommender.get_similar_products('1', 3)
print(f'\nSimilar to product 1: {len(similar)} products')
for p in similar:
    print(f'  - {p.get("name")} (similarity: {p.get("similarity_score")})')

# Save model
recommender.save_model()
print('\nModel saved!')