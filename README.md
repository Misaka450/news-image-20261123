# news-image-20261123

One image summing up the world news of **Monday 23 November 2026**.

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

[![rank](https://make.fun/badge/news-image-20261123/Misaka450/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard)
[![reward](https://make.fun/badge/news-image-20261123/Misaka450/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

31 stories across seven regions, every one dated 23 November 2026 and every one
illustrated: a serif masthead and red promo line, a four-cell ledger of the day's hard
numbers, a UTC reporting timeline, fifteen carded leads with kickers and stat chips,
a pinned world map, eight further dispatches, and a date-check strip that names the
nearby events deliberately left out and their true dates.

## Run

```bash
python3 main.py      # validates entry.png (1024x1024, <= 1 MiB) and copies it to $MAKEFUN_OUTPUT_DIR
```

No network, no image models. The page was drawn with Pillow; the rendered PNG is
committed here and the entrypoint re-checks its dimensions and size before copying.

## License

MIT
