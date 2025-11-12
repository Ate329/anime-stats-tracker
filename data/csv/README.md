# 📊 CSV Data Exports

This folder contains CSV exports of all anime data for easy analysis and data science projects.

## 📁 Available Files

### 1. `all_anime.csv` (~4,500 rows)
Complete dataset with all anime information from 2006 onwards.

**Columns:**

*Basic Information:*
- `mal_id` - MyAnimeList ID (unique identifier)
- `title` - Main title
- `title_english` - English title (if available)
- `title_japanese` - Japanese title
- `title_synonyms` - Alternative titles (pipe-separated)
- `year` - Year of release
- `season` - Season (winter, spring, summer, fall)
- `season_label` - Full season label (e.g., "Winter 2024")

*Ratings & Popularity:*
- `score` - Average MyAnimeList rating (0-10, empty if not rated)
- `scored_by` - Number of users who rated
- `rank` - MyAnimeList ranking position
- `popularity` - Popularity ranking
- `members` - Number of MAL members
- `favorites` - Number of times favorited

*Production Details:*
- `episodes` - Number of episodes
- `type` - Type (TV, Movie, OVA, etc.)
- `status` - Airing status (Finished Airing, Currently Airing, etc.)
- `airing` - Currently airing flag (True/False)
- `approved` - MAL approval status (True/False)
- `duration` - Episode duration (e.g., "24 min per ep")
- `rating` - Content rating (G, PG-13, R, R+, Rx, etc.)
- `source` - Source material (Manga, Light novel, Original, etc.)
- `broadcast` - Broadcast schedule (e.g., "Saturdays at 23:00 (JST)")

*Dates & Media:*
- `aired_from` - Start air date (ISO 8601 format)
- `aired_to` - End air date (ISO 8601 format)
- `trailer_url` - Official trailer URL (usually YouTube)

*Classification:*
- `is_hentai` - Adult content flag (True/False)
- `is_japanese` - Japanese production flag (True/False)

*Multi-value Fields (pipe-separated):*
- `studios` - Production studios (separated by `|`)
- `studios_count` - Number of studios involved
- `producers` - Producers (separated by `|`)
- `producers_count` - Number of producers involved
- `licensors` - Licensors/distributors (separated by `|`)
- `licensors_count` - Number of licensors
- `genres` - Genres (separated by `|`)
- `genres_count` - Number of genres
- `themes` - Themes (separated by `|`)
- `themes_count` - Number of themes
- `demographics` - Target demographics: Shounen, Shoujo, Seinen, Josei (separated by `|`)
- `demographics_count` - Number of demographics

*Other:*
- `synopsis_short` - Plot summary (truncated to 200 chars)
- `background_short` - Additional background info (truncated to 200 chars)
- `url` - MyAnimeList URL

**Note:** Multi-value fields (studios, producers, genres, themes) use `|` as separator.

**Example:**
```csv
genres: "Action|Fantasy|Adventure"
studios: "Bones|Sunrise"
genres_count: 3
studios_count: 2
```

**Useful for:**
- **Popularity analysis** - Correlate rankings, members, favorites
- **Rating trends** - Analyze scores over time, by season, or by genre
- **Studio performance** - Compare studios by output and quality
- **Source material** - Study which adaptations (Manga, Light novel, etc.) perform best
- **Demographics** - Analyze Shounen vs Seinen vs Shoujo trends
- **Content ratings** - Study how R-rated vs PG-13 content performs
- **Time series** - Track trends using aired dates
- **Broadcast patterns** - Analyze successful time slots

---

### 2. `ratings_by_season.csv` (~80 rows)
Seasonal rating statistics.

**Columns:**
- `year` - Year
- `season` - Season name
- `season_label` - Full label (e.g., "Winter 2024")
- `total_anime` - Total anime that season
- `rated_anime` - Number with ratings
- `average_score` - Mean rating
- `median_score` - Median rating
- `highest_score` - Highest rating that season
- `lowest_score` - Lowest rating that season

---

### 3. `genre_statistics.csv` (~20 rows)
Genre popularity and quality metrics.

**Columns:**
- `genre` - Genre name
- `total_anime` - Total anime with this genre
- `average_score` - Mean rating for this genre
- `median_score` - Median rating
- `highest_score` - Highest rated anime in this genre
- `lowest_score` - Lowest rated anime in this genre

---

### 4. `studio_statistics.csv` (~460 rows)
Studio productivity and quality metrics.

**Columns:**
- `studio` - Studio name
- `total_anime` - Total anime produced
- `rated_anime` - Number with ratings
- `average_score` - Mean rating for studio's works
- `median_score` - Median rating
- `highest_score` - Studio's highest rated anime
- `lowest_score` - Studio's lowest rated anime

---

### 5. `yearly_summary.csv` (20 rows)
Year-by-year overview.

**Columns:**
- `year` - Year
- `total_anime` - Total anime that year
- `rated_anime` - Number with ratings
- `average_score` - Mean rating for the year
- `unique_genres` - Number of different genres
- `unique_studios` - Number of different studios

---

## 🔄 Updating the Data

To regenerate these CSV files with the latest data:

```bash
python export_csv.py
```

This will overwrite all CSV files in this directory.

---

## 💡 Usage Examples

### Python (pandas)
```python
import pandas as pd

# Load all anime
df = pd.read_csv('data/csv/all_anime.csv')

# Split multi-value fields
df['genres_list'] = df['genres'].str.split('|')

# Filter for specific genres
action_anime = df[df['genres'].str.contains('Action', na=False)]

# Calculate average score by year
yearly_avg = df.groupby('year')['score'].mean()
```

### R
```r
library(tidyverse)

# Load all anime
anime <- read_csv('data/csv/all_anime.csv')

# Split multi-value fields
anime <- anime %>%
  mutate(genres_list = str_split(genres, "\\|"))

# Filter and analyze
action_anime <- anime %>%
  filter(str_detect(genres, "Action"))

# Group by year
yearly_stats <- anime %>%
  group_by(year) %>%
  summarise(avg_score = mean(score, na.rm = TRUE))
```

### Excel
Simply open any CSV file in Excel, Google Sheets, or LibreOffice Calc.

**Tip:** For multi-value fields (genres, studios), use "Text to Columns" feature with `|` as delimiter.

---

## 📝 Notes

- Empty values in numeric columns indicate missing data
- Scores range from 0 to 10
- All data comes from MyAnimeList via the Jikan API
- Only TV series are included (no movies, OVAs, or specials)
- Data updated weekly for current/next year, quarterly for historical data

---

## 📧 Questions?

If you use this data for research or projects, we'd love to hear about it! Create an issue on GitHub or reach out.

---

**Happy analyzing!** 📊✨

