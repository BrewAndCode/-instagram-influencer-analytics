"""
Generate a synthetic test dataset to validate the pipeline works end-to-end.
This creates a realistic raw CSV that mimics what collect.py would produce.

DO NOT use this data as real data — it is for pipeline testing only.
"""

import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta

# Seed for reproducibility
random.seed(42)

# Categories of realistic-looking (but synthetic) test profiles
CATEGORIES = {
    'food': {
        'bios': [
            'Home cook 🍳 | Sharing my kitchen adventures | DM for collabs',
            'Recipe developer & food photographer 📸 | foodie4life@email.com',
            'Plant-based recipes | NYC | Spreading food love 🌱',
            'Chef in training | Baking enthusiast | All recipes tested by me',
            'Street food explorer | Tasting the world one bite at a time',
        ],
        'hashtags': ['foodie', 'homecooking', 'recipe', 'foodphotography', 'instafood',
                     'yummy', 'cooking', 'baking', 'healthyfood', 'mealprep'],
    },
    'fitness': {
        'bios': [
            'NASM Certified PT | Transform your body 💪 | Link in bio',
            'Yoga teacher | Mindfulness | Based in LA | workshops@yoga.com',
            'Marathon runner | 5AM club | Fitness is a lifestyle',
            'Calisthenics athlete | No gym needed | Free workout plans ⬇️',
            'Pilates instructor | Body positivity | Move with joy',
        ],
        'hashtags': ['fitness', 'workout', 'gym', 'fitnessmotivation', 'health',
                     'exercise', 'yoga', 'running', 'bodybuilding', 'wellness'],
    },
    'travel': {
        'bios': [
            'Wanderlust 🌍 | 45 countries | travel.adventures@gmail.com',
            'Budget travel tips | Digital nomad | Currently in Bali',
            'Luxury travel & hotels | DM for partnerships',
            'Adventure seeker | Mountains > beaches | Canon R5',
            'Solo female traveler | Safety tips | Inspiring wanderlust',
        ],
        'hashtags': ['travel', 'wanderlust', 'explore', 'travelgram', 'adventure',
                     'vacation', 'travelphotography', 'digitalnomad', 'backpacking', 'tourism'],
    },
    'fashion': {
        'bios': [
            'Style blogger | Sustainable fashion ♻️ | Based in London',
            'OOTD daily | Thrift finds | Fashion student',
            'Menswear | Minimal style | Collabs: hello@stylepage.com',
            'Plus size fashion | Body positive | Dress for yourself 👗',
            'Streetwear culture | Sneaker collector | NYC',
        ],
        'hashtags': ['fashion', 'style', 'ootd', 'streetwear', 'outfit',
                     'fashionblogger', 'sustainable', 'mensfashion', 'thriftfinds', 'lookbook'],
    },
    'tech': {
        'bios': [
            'Tech reviewer | Gadget lover | techguy@reviews.com',
            'Software dev by day, content creator by night 💻',
            'AI & ML enthusiast | Breaking down complex topics',
            'Smartphone photography tips | Camera comparison reviews',
            'PC builder | Gaming setups | Honest reviews only',
        ],
        'hashtags': ['tech', 'technology', 'gadgets', 'programming', 'coding',
                     'developer', 'ai', 'smartphone', 'review', 'pcbuild'],
    },
    'photography': {
        'bios': [
            'Landscape photographer | Sony A7IV | Prints available',
            'Portrait & wedding photography | Bookings open 2025',
            'Street photography | Finding beauty in the mundane',
            'Astrophotography | Chasing the Milky Way | tutorials@astro.com',
            'Minimalist photography | Less is more | Canon user',
        ],
        'hashtags': ['photography', 'photographer', 'photooftheday', 'landscape',
                     'portrait', 'streetphotography', 'naturephotography', 'camera', 'lightroom', 'editing'],
    },
}


def generate_post_dates(count: int = 10, days_back: int = 90) -> list:
    """Generate realistic post dates."""
    now = datetime.now()
    dates = []
    for _ in range(count):
        offset = random.randint(1, days_back)
        date = now - timedelta(days=offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        dates.append(date.isoformat())
    dates.sort(reverse=True)
    return dates


def generate_profile(index: int) -> dict:
    """Generate a single synthetic test profile."""
    category = random.choice(list(CATEGORIES.keys()))
    cat_data = CATEGORIES[category]
    
    followers = random.choice([
        random.randint(500, 5000),       # nano
        random.randint(5000, 50000),     # micro
        random.randint(50000, 200000),   # mid
        random.randint(200000, 999999),  # macro (< 1M)
    ])
    
    # Generate realistic engagement (smaller accounts tend to have higher rates)
    if followers < 5000:
        avg_likes = int(followers * random.uniform(0.03, 0.15))
        avg_comments = int(followers * random.uniform(0.005, 0.02))
    elif followers < 50000:
        avg_likes = int(followers * random.uniform(0.02, 0.08))
        avg_comments = int(followers * random.uniform(0.002, 0.01))
    else:
        avg_likes = int(followers * random.uniform(0.01, 0.04))
        avg_comments = int(followers * random.uniform(0.001, 0.005))
    
    username = f"test_{category}_{index:04d}"
    bio = random.choice(cat_data['bios'])
    selected_hashtags = random.sample(cat_data['hashtags'], min(7, len(cat_data['hashtags'])))
    post_dates = generate_post_dates(count=random.randint(5, 10))
    
    # Occasionally add edge cases
    is_private = False
    collection_errors = None
    
    # ~5% chance of edge cases
    roll = random.random()
    if roll < 0.02:
        is_private = True
        collection_errors = f"Profile {username} is private."
    elif roll < 0.04:
        followers = random.randint(1000000, 5000000)  # Over 1M (should be filtered)
    elif roll < 0.05:
        avg_likes = None  # Missing data
        avg_comments = None
    
    return {
        'profile_url': f'https://www.instagram.com/{username}/',
        'name': f'Test User {index}',
        'username': username,
        'followers': followers,
        'following': random.randint(100, 3000),
        'bio': bio,
        'is_private': is_private,
        'is_verified': random.random() < 0.05,
        'media_count': random.randint(50, 2000),
        'avg_likes_last_10': avg_likes,
        'avg_comments_last_10': avg_comments,
        'post_dates_json': json.dumps(post_dates),
        'hashtags_json': json.dumps(selected_hashtags),
        'contact_details': _extract_contact(bio),
        'data_source': 'synthetic_test',
        'collection_date': datetime.now().isoformat(),
        'collection_errors': collection_errors,
    }


def _extract_contact(bio: str) -> str:
    """Extract email-like patterns from bio for test data."""
    import re
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', bio)
    if emails:
        return ', '.join(emails)
    return 'Not publicly available'


def generate_test_dataset(count: int = 30) -> str:
    """Generate a synthetic test dataset and save to data/raw/."""
    profiles = []
    
    for i in range(count):
        profiles.append(generate_profile(i))
    
    # Add a few deliberate duplicates for testing
    if count > 5:
        profiles.append(profiles[0].copy())  # Exact duplicate
        profiles.append(profiles[2].copy())  # Another duplicate
    
    df = pd.DataFrame(profiles)
    
    os.makedirs('data/raw', exist_ok=True)
    output_path = 'data/raw/test_raw_profiles.csv'
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} synthetic test profiles → {output_path}")
    print(f"  Includes {count} unique profiles + 2 deliberate duplicates")
    print(f"  Categories represented: {list(CATEGORIES.keys())}")
    
    return output_path


if __name__ == '__main__':
    output = generate_test_dataset(count=30)
    print(f"\nTest dataset ready at: {output}")
    print("Run the pipeline with:")
    print(f"  python src/pipeline.py --mode clean_only --input-file {output}")
