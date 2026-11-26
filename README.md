# kermis
8bit game

## HTML games

Two browser versions, each a single self-contained file (pixel art, fonts and the "Beat The Clown" soundtrack built in). Open one in any browser or play them on GitHub Pages:

- [Clown Invaders](https://mathewnephews.github.io/kermis/games/clown-invaders.html): Space Invaders style. Pie the band before they reach the midway, hiding behind the rides. Hit the bear balloon for double pies.
- [Beat The Clown](https://mathewnephews.github.io/kermis/games/): time attack scroller. Pie all band members as fast as you can, with one more band member every level.

Shared high scores: on a server with PHP 7.4+ and SQLite, `scores.php` keeps a top 10 per game that every player sees (name, country flag, score). Scores are stored in `games/data/`, which is locked by its `.htaccess`. On GitHub Pages there is no PHP, so the games fall back to each player's own scores. Set `ADMIN_KEY` in `scores.php` to switch on the admin page (`scores.php?admin=YOUR_KEY`) for deleting scores.

Controls: arrow keys or A/D to move, Space to throw, X for a super pie (Beat The Clown), P to pause, M for music. On phones, on-screen buttons appear.
