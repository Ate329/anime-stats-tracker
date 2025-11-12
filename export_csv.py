"""
Export anime data to CSV format for easy data analysis.
Creates comprehensive CSV files from the JSON data.
"""

import json
import csv
import pathlib
import statistics
from datetime import datetime

# Configuration
DATA_DIR = pathlib.Path("data")
OUTPUT_DIR = pathlib.Path("data/csv")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_all_anime_data():
    """Load all anime data from JSON files."""
    all_anime = []
    manifest_path = DATA_DIR / "manifest.json"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    for entry in manifest:
        year = entry['year']
        season = entry['season']
        file_path = DATA_DIR / str(year) / f"{season}.json"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                anime_list = json.load(f)
                all_anime.extend(anime_list)
    
    return all_anime

def export_all_anime():
    """Export all anime data to a comprehensive CSV file."""
    print("\nExporting all anime data to CSV...")
    
    all_anime = load_all_anime_data()
    current_year = datetime.now().year
    
    # Filter to valid years
    valid_anime = [a for a in all_anime if a.get('year') and 2006 <= a.get('year') <= current_year]
    
    output_path = OUTPUT_DIR / "all_anime.csv"
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header - all available fields from Jikan API
        writer.writerow([
            'mal_id',
            'title',
            'title_english',
            'title_japanese',
            'title_synonyms',
            'year',
            'season',
            'season_label',
            'score',
            'scored_by',
            'rank',
            'popularity',
            'members',
            'favorites',
            'episodes',
            'type',
            'status',
            'airing',
            'approved',
            'duration',
            'rating',
            'source',
            'broadcast',
            'aired_from',
            'aired_to',
            'trailer_url',
            'is_hentai',
            'is_japanese',
            'studios',
            'studios_count',
            'producers',
            'producers_count',
            'licensors',
            'licensors_count',
            'genres',
            'genres_count',
            'themes',
            'themes_count',
            'demographics',
            'demographics_count',
            'synopsis_short',
            'background_short',
            'url'
        ])
        
        # Data rows
        for anime in valid_anime:
            studios = anime.get('studios', [])
            producers = anime.get('producers', [])
            licensors = anime.get('licensors', [])
            genres = anime.get('genres', [])
            themes = anime.get('themes', [])
            demographics = anime.get('demographics', [])
            title_synonyms = anime.get('title_synonyms', [])
            
            synopsis = (anime.get('synopsis', '') or '').replace('\n', ' ').replace('\r', ' ')
            background = (anime.get('background', '') or '').replace('\n', ' ').replace('\r', ' ')
            
            # Truncate long text fields for easier CSV handling
            synopsis_short = synopsis[:200] + '...' if len(synopsis) > 200 else synopsis
            background_short = background[:200] + '...' if len(background) > 200 else background
            
            season_label = f"{anime.get('season', '').capitalize()} {anime.get('year', '')}"
            
            writer.writerow([
                anime.get('mal_id', ''),
                anime.get('title', ''),
                anime.get('title_english', ''),
                anime.get('title_japanese', ''),
                '|'.join(title_synonyms),
                anime.get('year', ''),
                anime.get('season', ''),
                season_label,
                anime.get('score', ''),
                anime.get('scored_by', ''),
                anime.get('rank', ''),
                anime.get('popularity', ''),
                anime.get('members', ''),
                anime.get('favorites', ''),
                anime.get('episodes', ''),
                anime.get('type', ''),
                anime.get('status', ''),
                anime.get('airing', ''),
                anime.get('approved', ''),
                anime.get('duration', ''),
                anime.get('rating', ''),
                anime.get('source', ''),
                anime.get('broadcast', ''),
                anime.get('aired_from', ''),
                anime.get('aired_to', ''),
                anime.get('trailer_url', ''),
                anime.get('is_hentai', ''),
                anime.get('is_japanese', ''),
                '|'.join(studios),
                len(studios),
                '|'.join(producers),
                len(producers),
                '|'.join(licensors),
                len(licensors),
                '|'.join(genres),
                len(genres),
                '|'.join(themes),
                len(themes),
                '|'.join(demographics),
                len(demographics),
                synopsis_short,
                background_short,
                anime.get('url', '')
            ])
    
    print(f"[OK] Exported {len(valid_anime)} anime to {output_path}")

def export_ratings_by_season():
    """Export seasonal ratings summary to CSV."""
    print("\nExporting seasonal ratings to CSV...")
    
    manifest_path = DATA_DIR / "manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    output_path = OUTPUT_DIR / "ratings_by_season.csv"
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'year',
            'season',
            'season_label',
            'total_anime',
            'rated_anime',
            'average_score',
            'median_score',
            'highest_score',
            'lowest_score'
        ])
        
        # Data rows
        for entry in manifest:
            year = entry['year']
            season = entry['season']
            
            if year < 2006 or year > datetime.now().year:
                continue
            
            season_file = DATA_DIR / str(year) / f"{season}.json"
            
            if season_file.exists():
                with open(season_file, 'r', encoding='utf-8') as sf:
                    anime_list = json.load(sf)
                
                total_anime = len(anime_list)
                scores = [a['score'] for a in anime_list if a.get('score') is not None]
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    median_score = statistics.median(scores)
                    highest = max(scores)
                    lowest = min(scores)
                else:
                    avg_score = median_score = highest = lowest = None
                
                writer.writerow([
                    year,
                    season,
                    f"{season.capitalize()} {year}",
                    total_anime,
                    len(scores),
                    round(avg_score, 2) if avg_score else '',
                    round(median_score, 2) if median_score else '',
                    highest if highest else '',
                    lowest if lowest else ''
                ])
    
    print(f"[OK] Exported seasonal ratings to {output_path}")

def export_genre_statistics():
    """Export genre statistics to CSV."""
    print("\nExporting genre statistics to CSV...")
    
    all_anime = load_all_anime_data()
    current_year = datetime.now().year
    valid_anime = [a for a in all_anime if a.get('year') and 2006 <= a.get('year') <= current_year]
    
    # Count genres
    genre_counts = {}
    genre_scores = {}
    
    for anime in valid_anime:
        genres = anime.get('genres', [])
        score = anime.get('score')
        
        for genre in genres:
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                if score:
                    if genre not in genre_scores:
                        genre_scores[genre] = []
                    genre_scores[genre].append(score)
    
    output_path = OUTPUT_DIR / "genre_statistics.csv"
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'genre',
            'total_anime',
            'average_score',
            'median_score',
            'highest_score',
            'lowest_score'
        ])
        
        # Sort by count descending
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        
        for genre, count in sorted_genres:
            scores = genre_scores.get(genre, [])
            if scores:
                avg = sum(scores) / len(scores)
                median = statistics.median(scores)
                highest = max(scores)
                lowest = min(scores)
            else:
                avg = median = highest = lowest = None
            
            writer.writerow([
                genre,
                count,
                round(avg, 2) if avg else '',
                round(median, 2) if median else '',
                highest if highest else '',
                lowest if lowest else ''
            ])
    
    print(f"[OK] Exported genre statistics to {output_path}")

def export_studio_statistics():
    """Export studio statistics to CSV."""
    print("\nExporting studio statistics to CSV...")
    
    all_anime = load_all_anime_data()
    current_year = datetime.now().year
    valid_anime = [a for a in all_anime if a.get('year') and 2006 <= a.get('year') <= current_year]
    
    # Count studios
    studio_counts = {}
    studio_scores = {}
    
    for anime in valid_anime:
        studios = anime.get('studios', [])
        score = anime.get('score')
        
        for studio in studios:
            if studio:
                studio_counts[studio] = studio_counts.get(studio, 0) + 1
                if score:
                    if studio not in studio_scores:
                        studio_scores[studio] = []
                    studio_scores[studio].append(score)
    
    output_path = OUTPUT_DIR / "studio_statistics.csv"
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'studio',
            'total_anime',
            'rated_anime',
            'average_score',
            'median_score',
            'highest_score',
            'lowest_score'
        ])
        
        # Sort by count descending
        sorted_studios = sorted(studio_counts.items(), key=lambda x: x[1], reverse=True)
        
        for studio, count in sorted_studios:
            scores = studio_scores.get(studio, [])
            if scores:
                avg = sum(scores) / len(scores)
                median = statistics.median(scores)
                highest = max(scores)
                lowest = min(scores)
            else:
                avg = median = highest = lowest = None
            
            writer.writerow([
                studio,
                count,
                len(scores),
                round(avg, 2) if avg else '',
                round(median, 2) if median else '',
                highest if highest else '',
                lowest if lowest else ''
            ])
    
    print(f"[OK] Exported studio statistics to {output_path}")

def export_yearly_summary():
    """Export yearly summary statistics to CSV."""
    print("\nExporting yearly summary to CSV...")
    
    all_anime = load_all_anime_data()
    current_year = datetime.now().year
    
    # Group by year
    yearly_data = {}
    
    for anime in all_anime:
        year = anime.get('year')
        if not year or year < 2006 or year > current_year:
            continue
        
        if year not in yearly_data:
            yearly_data[year] = {
                'total': 0,
                'scores': [],
                'genres': set(),
                'studios': set()
            }
        
        yearly_data[year]['total'] += 1
        
        score = anime.get('score')
        if score:
            yearly_data[year]['scores'].append(score)
        
        for genre in anime.get('genres', []):
            if genre:
                yearly_data[year]['genres'].add(genre)
        
        for studio in anime.get('studios', []):
            if studio:
                yearly_data[year]['studios'].add(studio)
    
    output_path = OUTPUT_DIR / "yearly_summary.csv"
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'year',
            'total_anime',
            'rated_anime',
            'average_score',
            'unique_genres',
            'unique_studios'
        ])
        
        # Sort by year
        for year in sorted(yearly_data.keys()):
            data = yearly_data[year]
            scores = data['scores']
            avg_score = sum(scores) / len(scores) if scores else None
            
            writer.writerow([
                year,
                data['total'],
                len(scores),
                round(avg_score, 2) if avg_score else '',
                len(data['genres']),
                len(data['studios'])
            ])
    
    print(f"[OK] Exported yearly summary to {output_path}")

def main():
    print("=" * 60)
    print("Exporting Anime Data to CSV")
    print("=" * 60)
    
    export_all_anime()
    export_ratings_by_season()
    export_genre_statistics()
    export_studio_statistics()
    export_yearly_summary()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All CSV exports completed!")
    print("=" * 60)
    print(f"\nCSV files saved to: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    main()

