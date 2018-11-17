# Run

First you need to generate your API key [here](https://comicvine.gamespot.com/api/). You will need to have an account to do this.

To collect only resources regarding movies (note: replace `y0urApIk3y` with your API key):
```bash
$ python collector.py -api-key y0urApIk3y -res movies
```

To collect all resources (note: replace `y0urApIk3y` with your API key):
```bash
$ python collector.py -api-key y0urApIk3y -res all
```

Only plural resources are collected. All resources include:  
- characters
- concepts
- episodes
- locations
- objects
- origins
- people
- powers
- promos
- publishers 
- series_list
- search
- story_arcs
- teams
- types
- videos
- video_types
- video_categories
- volumes
- movies
- issues