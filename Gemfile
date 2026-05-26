source "https://rubygems.org"

ruby "3.4.2"

gem "jekyll", "~> 4.4.1"

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-feed",    "~> 0.17"   # Atom/RSS feed for posts
  gem "jekyll-seo-tag", "~> 2.8"    # <meta> SEO tags
  gem "jekyll-sitemap", "~> 1.4"    # /sitemap.xml
end

# Windows/JRuby platform compatibility (safe to include everywhere)
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-boost for watching directories on Windows
gem "wdm", "~> 0.1", platforms: %i[mingw x64_mingw mswin]

# Lock `http_parser.rb` gem to a specific version on JRuby builds
gem "http_parser.rb", "~> 0.6.0", platforms: :jruby
