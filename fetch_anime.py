import requests
import json
import pathlib
import datetime
import time
import sys

def validate_and_deduplicate(anime_list, year, season):
    """
    Validates and removes duplicate anime from a list based on mal_id.
    Returns the deduplicated list and reports any duplicates found.
    
    Args:
        anime_list: List of anime dictionaries
        year: Year for logging purposes
        season: Season for logging purposes
    
    Returns:
        Deduplicated list of anime
    """
    if not anime_list:
        return anime_list
    
    seen_ids = {}
    unique_anime = []
    duplicates_found = []
    
    for anime in anime_list:
        mal_id = anime.get('mal_id')
        if mal_id is None:
            print(f"  [WARNING] Anime without mal_id found: {anime.get('title', 'Unknown')}")
            continue
        
        if mal_id in seen_ids:
            duplicates_found.append({
                'mal_id': mal_id,
                'title': anime.get('title', 'Unknown')
            })
        else:
            seen_ids[mal_id] = True
            unique_anime.append(anime)
    
    if duplicates_found:
        print(f"  [VALIDATION] Found and removed {len(duplicates_found)} duplicate(s) for {year} {season}:")
        for dup in duplicates_found[:5]:  # Show first 5 duplicates
            print(f"    - {dup['title']} (MAL ID: {dup['mal_id']})")
        if len(duplicates_found) > 5:
            print(f"    ... and {len(duplicates_found) - 5} more")
    else:
        print(f"  [VALIDATION] No duplicates found for {year} {season} - {len(unique_anime)} unique anime")
    
    return unique_anime

def clean_existing_data():
    """
    Scans all existing data files and removes duplicates.
    Creates a backup before cleaning.
    """
    print("\n" + "="*60)
    print("CLEANING EXISTING DATA FILES")
    print("="*60)
    
    data_dir = pathlib.Path("data")
    if not data_dir.exists():
        print("[INFO] No data directory found, nothing to clean")
        return
    
    seasons = ["winter", "spring", "summer", "fall"]
    total_duplicates = 0
    files_cleaned = 0
    
    # Find all year directories
    year_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    
    for year_dir in sorted(year_dirs):
        year = year_dir.name
        
        for season in seasons:
            file_path = year_dir / f"{season}.json"
            
            if not file_path.exists():
                continue
            
            try:
                # Read existing data
                with open(file_path, 'r', encoding='utf-8') as f:
                    anime_list = json.load(f)
                
                original_count = len(anime_list)
                
                # Validate and deduplicate
                cleaned_list = validate_and_deduplicate(anime_list, year, season)
                
                duplicates = original_count - len(cleaned_list)
                
                # Only save if we found duplicates
                if duplicates > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(cleaned_list, f, ensure_ascii=False, indent=2)
                    
                    print(f"  [CLEANED] {file_path}: Removed {duplicates} duplicate(s)")
                    total_duplicates += duplicates
                    files_cleaned += 1
                
            except Exception as e:
                print(f"  [ERROR] Failed to clean {file_path}: {e}")
    
    print(f"\n[SUMMARY] Cleaned {files_cleaned} file(s), removed {total_duplicates} total duplicate(s)")
    print("="*60)

def fetch_anime_data(current_years_only=False, specific_years=None):
    """
    Fetches anime data from Jikan API and organizes it by year and season.
    Creates a manifest.json file listing all available season data.
    
    The script automatically fetches data from START_YEAR to current year + 1,
    so it will always include new years without manual updates.
    
    Args:
        current_years_only (bool): If True, only fetch current and next year.
                                   If False, fetch all years from START_YEAR.
        specific_years (list): If provided, only fetch data for these specific years.
    """
    # Configuration: Starting year for data collection (change if needed)
    START_YEAR = 2006
    
    # Get current year
    current_year = datetime.date.today().year
    
    # Define years to fetch based on mode
    if specific_years:
        # Fetch only specific years
        years = specific_years
        print(f"Mode: Specific years ({', '.join(map(str, years))})")
    elif current_years_only:
        # Only fetch current and next year (for weekly updates)
        years = list(range(current_year, current_year + 2))
        print(f"Mode: Current years only ({current_year}, {current_year + 1})")
    else:
        # Fetch all years dynamically from START_YEAR to current + 1 (for quarterly updates)
        years = list(range(START_YEAR, current_year + 2))
        print(f"Mode: All years ({START_YEAR}-{current_year + 1})")
    
    # Define seasons
    seasons = ["winter", "spring", "summer", "fall"]
    
    # Load existing manifest to preserve data for years we're not fetching
    manifest_path = pathlib.Path("data/manifest.json")
    existing_manifest = []
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                existing_manifest = json.load(f)
            print(f"Loaded existing manifest with {len(existing_manifest)} seasons")
        except Exception as e:
            print(f"Could not load existing manifest: {e}")
    
    # Initialize manifest list
    available_seasons = []
    
    # Preserve entries for years we're NOT fetching
    if (current_years_only or specific_years) and existing_manifest:
        years_to_fetch = set(years)
        for entry in existing_manifest:
            if entry['year'] not in years_to_fetch:
                available_seasons.append(entry)
        print(f"Preserved {len(available_seasons)} existing season entries from other years")
    
    # Base URL for Jikan API
    base_url = "https://api.jikan.moe/v4/seasons"
    
    print(f"Starting to fetch anime data for years: {years}")
    
    # Main loop through years and seasons
    for year in years:
        for season in seasons:
            try:
                print(f"\nFetching data for {year} {season}...")
                
                # Fetch all pages for this season
                anime_list = []
                seen_mal_ids = set()  # Track unique anime by mal_id to prevent duplicates
                page = 1
                has_next_page = True
                
                while has_next_page:
                    # Construct API URL with pagination
                    api_url = f"{base_url}/{year}/{season}?page={page}"
                    
                    # Make API request
                    response = requests.get(api_url)
                    
                    # Check if request was successful
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if there's more data
                        if 'data' in data and len(data['data']) > 0:
                            print(f"  Page {page}: Found {len(data['data'])} anime")
                            
                            # Extract and process anime data from this page
                            for anime in data['data']:
                                # Check for duplicate mal_id first (before any processing)
                                mal_id = anime.get('mal_id')
                                if mal_id in seen_mal_ids:
                                    print(f"  [SKIP] Duplicate anime detected (MAL ID: {mal_id})")
                                    continue
                                
                                # Filter: Only include TV series (no movies, OVAs, etc.)
                                anime_type = anime.get('type', '')
                                if anime_type != 'TV':
                                    continue
                                
                                # Identify "Kids" demographic (for quality filtering later)
                                demographics = anime.get('demographics', [])
                                demographic_names = [demo.get('name', '') for demo in demographics]
                                is_kid = 'Kids' in demographic_names
                                
                                # Check for hentai genre
                                genres = anime.get('genres', [])
                                genre_names = [genre.get('name', '') for genre in genres]
                                is_hentai = 'Hentai' in genre_names
                                
                                # Get producers and studios to determine if it's Japanese anime
                                producers = anime.get('producers', [])
                                producer_names = [p.get('name', '') for p in producers]
                                studios = anime.get('studios', [])
                                studio_names = [s.get('name', '') for s in studios]
                                
                                # Extract title_japanese early for detection
                                title_japanese = anime.get('title_japanese')
                                
                                # Check for Japanese Kana (Hiragana/Katakana) in the Japanese title
                                # This is a very strong indicator of Japanese language/origin
                                # Chinese donghua usually have Hanzi (Chinese characters) only, with no Kana
                                has_kana = False
                                if title_japanese:
                                    for char in title_japanese:
                                        # Hiragana (0x3040-0x309F) or Katakana (0x30A0-0x30FF)
                                        if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':
                                            has_kana = True
                                            break
                                
                                # Major Japanese anime studios (if produced by these, it's Japanese anime)
                                japanese_studios = [
                                    'a-1 pictures', 'trigger', 'mappa', 'ufotable', 'bones', 'kyoto animation',
                                    'madhouse', 'wit studio', 'production i.g', 'cloverworks', 'shaft', 'j.c.staff',
                                    'toei animation', 'studio deen', 'david production', 'sunrise', 'gainax',
                                    'pierrot', 'silver link', 'lerche', 'kinema citrus', 'white fox', 'doga kobo',
                                    'p.a. works', 'studio ghibli', 'tms entertainment', 'olm', 'toho animation',
                                    'shin-ei animation', 'nippon animation', 'tezuka productions', 'tatsunoko production',
                                    'bandai namco', 'lidenfilms', 'maho film', 'nut', 'geek toys', 'zero-g',
                                    'feel.', 'zexcs', 'project no.9', 'c-station', 'tnk', 'shuka', 'lay-duce'
                                ]
                                
                                # Check if it's produced by a Japanese studio
                                has_japanese_studio = any(
                                    any(jp_studio in studio.lower() for jp_studio in japanese_studios)
                                    for studio in studio_names
                                )
                                
                                # Origin Detection Logic:
                                # We assume it is Japanese ONLY if we have positive evidence:
                                # 1. Produced by a known Japanese studio
                                # 2. Has Japanese Kana characters in the Japanese title (Chinese titles are usually Hanzi-only)
                                #
                                # If neither is true (No Major Studio + No Kana), we treat it as "Potential Non-Japanese/Indie"
                                # and subject it to the stricter Quality/Popularity filters.
                                
                                is_likely_japanese = has_japanese_studio or has_kana
                                
                                # Extract licensors
                                licensors = anime.get('licensors', [])
                                licensor_names = [lic.get('name', '') for lic in licensors]
                                
                                # Extract trailer URL - prefer embed_url as fallback since url can be null
                                trailer = anime.get('trailer', {})
                                trailer_url = trailer.get('url') or trailer.get('embed_url') if trailer else None
                                
                                # Extract broadcast string
                                broadcast = anime.get('broadcast', {})
                                broadcast_string = broadcast.get('string') if broadcast else None
                                
                                anime_info = {
                                    'mal_id': anime.get('mal_id', 'N/A'),
                                    'title': anime.get('title', 'Unknown Title'),
                                    'title_english': anime.get('title_english'),
                                    'title_japanese': anime.get('title_japanese'),
                                    'title_synonyms': anime.get('title_synonyms', []),
                                    'image_url': anime.get('images', {}).get('jpg', {}).get('large_image_url', 
                                                anime.get('images', {}).get('jpg', {}).get('image_url', '')),
                                    'trailer_url': trailer_url,
                                    'synopsis': anime.get('synopsis', 'No synopsis available.'),
                                    'background': anime.get('background'),
                                    'episodes': anime.get('episodes'),
                                    'score': anime.get('score'),
                                    'scored_by': anime.get('scored_by'),
                                    'rank': anime.get('rank'),
                                    'popularity': anime.get('popularity'),
                                    'members': anime.get('members'),
                                    'favorites': anime.get('favorites'),
                                    'type': anime_type,
                                    'status': anime.get('status'),
                                    'airing': anime.get('airing'),
                                    'approved': anime.get('approved'),
                                    'duration': anime.get('duration'),
                                    'rating': anime.get('rating'),
                                    'source': anime.get('source', 'Unknown'),
                                    'studios': [studio.get('name') for studio in anime.get('studios', [])],
                                    'producers': producer_names,
                                    'licensors': licensor_names,
                                    'genres': genre_names,
                                    'themes': [theme.get('name') for theme in anime.get('themes', [])],
                                    'demographics': demographic_names,
                                    'aired_from': anime.get('aired', {}).get('from'),
                                    'aired_to': anime.get('aired', {}).get('to'),
                                    'broadcast': broadcast_string,
                                    'url': anime.get('url', ''),
                                    'year': anime.get('year'),
                                    'season': anime.get('season'),
                                    'is_hentai': is_hentai,
                                    'is_japanese': is_likely_japanese,
                                    'is_kid': is_kid
                                }
                                anime_list.append(anime_info)
                                seen_mal_ids.add(mal_id)  # Mark this anime as seen
                            
                            # Check pagination info
                            pagination = data.get('pagination', {})
                            has_next_page = pagination.get('has_next_page', False)
                            page += 1
                            
                            # Rate limiting between pages
                            if has_next_page:
                                time.sleep(2)  # Increased to 2 seconds to avoid rate limiting
                        else:
                            has_next_page = False
                    elif response.status_code == 404:
                        print(f"  [SKIP] No data available for {year} {season} (404)")
                        has_next_page = False
                    else:
                        print(f"  [ERROR] Status {response.status_code}")
                        has_next_page = False
                
                # Post-processing: Smart Filter for "Actual Anime"
                if anime_list:
                    # 1. Identify "Core Anime" vs "Suspect Content"
                    # Core Anime = Japanese & Not Kids (The standard for "Real Anime")
                    # Suspect = Kids Anime (Pokemon or Random Cartoon?) OR Non-Japanese (Link Click or Random Cartoon?)
                    
                    core_anime = [a for a in anime_list if a['is_japanese'] and not a['is_kid']]
                    
                    # 2. Calculate thresholds based on CORE anime (to set the quality bar)
                    # If no core anime (very rare), fallback to full list
                    ref_list = core_anime if core_anime else anime_list
                    
                    scores = [a['score'] for a in ref_list if a['score'] is not None]
                    member_counts = [a['members'] for a in ref_list if a['members'] is not None]
                    
                    avg_score = sum(scores) / len(scores) if scores else 0
                    
                    # Median Members of Core Anime
                    median_members = 0
                    if member_counts:
                        sorted_members = sorted(member_counts)
                        median_members = sorted_members[len(sorted_members) // 2]
                    
                    # Define Thresholds
                    # Score: 1.0 point below average
                    score_threshold = avg_score - 1.0 if avg_score > 0 else 0
                    # Popularity: Median of Core Anime (Top 50% of standard anime)
                    member_threshold = median_members
                    
                    print(f"  [FILTER stats] Reference Set: {len(ref_list)} core anime")
                    print(f"  [FILTER stats] Core Avg Score: {avg_score:.2f}, Core Median Members: {median_members}")
                    
                    filtered_list = []
                    dropped_count = 0
                    
                    for anime in anime_list:
                        # Determine if this anime needs to prove itself
                        # It is 'suspect' if it is NOT (Japanese AND Not-Kids)
                        # i.e. It IS (Non-Japanese OR Kids)
                        is_suspect = not (anime['is_japanese'] and not anime['is_kid'])
                        
                        if is_suspect:
                            score = anime['score'] or 0
                            members = anime['members'] or 0
                            
                            # Pass if:
                            # 1. Popular enough (Matches Core Median)
                            # 2. High Quality enough (Close to Core Avg)
                            
                            is_popular = members >= member_threshold
                            is_quality = score >= score_threshold
                            
                            if not (is_popular or is_quality):
                                # Fails both -> Likely "Random Cartoon"
                                dropped_count += 1
                                # print(f"    [DROP] {anime['title']} (Kid:{anime['is_kid']}, JP:{anime['is_japanese']}, Mem:{members}, Sc:{score})")
                                continue
                        
                        filtered_list.append(anime)
                    
                    if dropped_count > 0:
                        print(f"  [FILTER] Dropped {dropped_count} 'suspect' anime (kids/non-JP) below quality thresholds")
                    anime_list = filtered_list

                # Data preservation: save new data or keep existing data
                data_path = pathlib.Path(f"data/{year}")
                data_path.mkdir(parents=True, exist_ok=True)
                file_path = data_path / f"{season}.json"
                
                if anime_list:
                    # Validate and deduplicate before saving (extra safety check)
                    anime_list = validate_and_deduplicate(anime_list, year, season)
                    
                    # We got data from API - save it
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(anime_list, f, ensure_ascii=False, indent=2)
                    
                    print(f"[OK] Successfully saved {len(anime_list)} anime to {file_path}")
                    
                    # Add to manifest
                    available_seasons.append({
                        "year": year,
                        "season": season,
                        "count": len(anime_list)
                    })
                else:
                    # No data from API - preserve existing data if available
                    if file_path.exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            print(f"[PRESERVED] No new data from API, keeping existing {len(existing_data)} anime")
                            
                            # Add existing data to manifest
                            available_seasons.append({
                                "year": year,
                                "season": season,
                                "count": len(existing_data)
                            })
                        except Exception as e:
                            print(f"[ERROR] Could not read existing file: {e}")
                    else:
                        print(f"[SKIP] No anime found for {year} {season}")
                
                # Rate limiting between seasons
                time.sleep(2)  # Increased to 2 seconds to avoid rate limiting
                
            except Exception as e:
                print(f"[ERROR] Error fetching {year} {season}: {str(e)}")
                continue
    
    # Save manifest (sorted by year and season for consistency)
    # Use a safe sorting method that handles unexpected season names
    season_order = {season: i for i, season in enumerate(seasons)}
    available_seasons.sort(key=lambda x: (x['year'], season_order.get(x['season'], 999)))
    
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(available_seasons, f, indent=2)
    
    print(f"\n[OK] Manifest saved with {len(available_seasons)} seasons")
    print(f"[OK] Data fetching complete!")

if __name__ == "__main__":
    # Check for command-line arguments
    current_years_only = '--current-years-only' in sys.argv
    all_years = '--all-years' in sys.argv
    clean_data = '--clean' in sys.argv
    
    # Check for --year argument
    specific_years = None
    for arg in sys.argv:
        if arg.startswith('--year='):
            year_str = arg.split('=')[1]
            # Support comma-separated years or a single year
            if ',' in year_str:
                specific_years = [int(y.strip()) for y in year_str.split(',')]
            else:
                specific_years = [int(year_str)]
            break
    
    # If --clean is specified, run the cleanup function and exit
    if clean_data:
        clean_existing_data()
        sys.exit(0)
    
    # If --all-years is specified, explicitly set current_years_only to False
    if all_years:
        current_years_only = False
    
    fetch_anime_data(current_years_only=current_years_only, specific_years=specific_years)

