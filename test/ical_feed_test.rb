# frozen_string_literal: true

# Tests for _plugins/ical_feed.rb. Each test builds a throwaway Jekyll site
# in a temp dir with the plugin loaded and inspects the generated .ics.
#
# Run: bin/test

require "minitest/autorun"
require "minitest/mock"
require "jekyll"
require "tmpdir"
require "fileutils"
require "yaml"

class IcalFeedTest < Minitest::Test
  PLUGINS_DIR = File.expand_path("../_plugins", __dir__)

  def setup
    @source = Dir.mktmpdir("ical-feed-src")
    @dest = Dir.mktmpdir("ical-feed-site")
  end

  def teardown
    FileUtils.rm_rf([@source, @dest])
  end

  # --- helpers ---------------------------------------------------------------

  def write(path, content)
    file = File.join(@source, path)
    FileUtils.mkdir_p(File.dirname(file))
    File.write(file, content)
  end

  def data(name, value)
    write("_data/#{name}.yml", YAML.dump(value))
  end

  def build(feeds, **config)
    site_config = {
      "source" => @source,
      "destination" => @dest,
      "plugins_dir" => PLUGINS_DIR,
      "url" => "https://example.org",
      "title" => "Example",
      "timezone" => "UTC",
      "quiet" => true,
      "ical_feeds" => feeds,
    }.merge(config.transform_keys(&:to_s))
    Jekyll::Site.new(Jekyll.configuration(site_config)).tap(&:process)
  end

  def read(path = "feed.ics")
    File.read(File.join(@dest, path), encoding: "UTF-8")
  end

  def warnings
    messages = []
    Jekyll.logger.stub(:warn, ->(topic, message = nil) { messages << "#{topic} #{message}" }) { yield }
    messages.join("\n")
  end

  # RFC 5545 unfolding, so assertions don't depend on where lines break.
  def unfolded(path = "feed.ics")
    read(path).gsub("\r\n ", "").split("\r\n")
  end

  def events(path = "feed.ics")
    unfolded(path).slice_before("BEGIN:VEVENT").drop(1).map do |lines|
      lines.take_while { |l| l != "END:VEVENT" }.drop(1).to_h { |l| l.split(":", 2) }
    end
  end

  def feed(**options)
    { "path" => "feed.ics", "source" => "data:events" }.merge(options.transform_keys(&:to_s))
  end

  # --- calendar --------------------------------------------------------------

  def test_writes_a_valid_calendar_envelope
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    build([feed(name: "My Talks", timezone: "Europe/Berlin", refresh: "PT6H")])

    lines = unfolded
    assert_equal "BEGIN:VCALENDAR", lines.first
    assert_equal "END:VCALENDAR", lines.last
    assert_includes lines, "VERSION:2.0"
    assert_includes lines, "X-WR-CALNAME:My Talks"
    assert_includes lines, "X-WR-TIMEZONE:Europe/Berlin"
    assert_includes lines, "REFRESH-INTERVAL;VALUE=DURATION:PT6H"
    assert read.end_with?("\r\n"), "lines must be CRLF-terminated"
  end

  def test_calendar_name_defaults_to_site_title
    data("events", [])
    build([feed])

    assert_includes unfolded, "X-WR-CALNAME:Example"
  end

  def test_writes_feed_to_nested_path_and_keeps_it_out_of_the_sitemap
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    site = build([feed(path: "cal/talks.ics")])

    assert File.exist?(File.join(@dest, "cal/talks.ics"))
    page = site.pages.find { |p| p.url == "/cal/talks.ics" }
    assert_equal false, page.data["sitemap"]
  end

  def test_supports_multiple_feeds
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    data("other", [{ "date" => "2026-11-06", "title" => "B" }])
    build([feed(path: "a.ics"), feed(path: "b.ics", source: "data:other")])

    assert_equal "A", events("a.ics").first["SUMMARY"]
    assert_equal "B", events("b.ics").first["SUMMARY"]
  end

  # --- dates and times -------------------------------------------------------

  def test_date_only_becomes_all_day_event
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    build([feed])

    event = events.first
    assert_equal "20261105", event["DTSTART;VALUE=DATE"]
    assert_equal "20261106", event["DTEND;VALUE=DATE"]
  end

  def test_datetime_becomes_timed_event_in_utc_using_duration
    data("events", [{ "date" => "2026-11-05T18:30:00+01:00", "duration" => 90, "title" => "A" }])
    build([feed])

    event = events.first
    assert_equal "20261105T173000Z", event["DTSTART"]
    assert_equal "20261105T190000Z", event["DTEND"]
  end

  def test_timed_event_without_end_or_duration_lasts_one_hour
    data("events", [{ "date" => "2026-11-05T10:00:00Z", "title" => "A" }])
    build([feed])

    assert_equal "20261105T110000Z", events.first["DTEND"]
  end

  def test_explicit_end_wins_over_duration
    data("events", [{ "date" => "2026-11-05T10:00:00Z", "end" => "2026-11-05T12:15:00Z", "duration" => 30, "title" => "A" }])
    build([feed])

    assert_equal "20261105T121500Z", events.first["DTEND"]
  end

  def test_all_day_true_drops_the_time
    data("events", [{ "date" => "2026-11-05T10:00:00Z", "title" => "A" }])
    build([feed(all_day: true)])

    assert_equal "20261105", events.first["DTSTART;VALUE=DATE"]
  end

  def test_all_day_false_keeps_midnight_as_a_time
    data("events", [{ "date" => "2026-11-05T00:00:00Z", "title" => "A" }])
    build([feed(all_day: false)])

    assert_equal "20261105T000000Z", events.first["DTSTART"]
  end

  def test_events_are_sorted_by_start
    data("events", [
      { "date" => "2026-12-01", "title" => "Later" },
      { "date" => "2026-01-01", "title" => "Earlier" },
    ])
    build([feed])

    assert_equal %w[Earlier Later], events.map { |e| e["SUMMARY"] }
  end

  def test_items_without_start_are_skipped
    data("events", [{ "title" => "No date" }, { "date" => "2026-11-05", "title" => "A" }])
    build([feed])

    assert_equal ["A"], events.map { |e| e["SUMMARY"] }
  end

  # --- sources ---------------------------------------------------------------

  def test_nested_data_path
    data("events", { "2026" => [{ "date" => "2026-11-05", "title" => "Nested" }] })
    build([feed(source: "data:events.2026")])

    assert_equal "Nested", events.first["SUMMARY"]
  end

  def test_collection_source_uses_front_matter_and_absolute_document_url
    write("_talks/konf.md", "---\ntitle: Konf\ndate: 2026-12-01\n---\nBody\n")
    build([feed(source: "collection:talks")],
          collections: { "talks" => { "output" => true } }, baseurl: "/blog")

    event = events.first
    assert_equal "Konf", event["SUMMARY"]
    assert_equal "20261201", event["DTSTART;VALUE=DATE"], "front matter date (midnight Time) should be all-day"
    assert_equal "https://example.org/blog/talks/konf.html", event["URL"]
  end

  def test_posts_source
    # Past date: Jekyll skips future-dated posts unless `future: true`.
    write("_posts/2020-11-05-hello.md", "---\ntitle: Hello\n---\nBody\n")
    build([feed(source: "posts")])

    assert_equal "Hello", events.first["SUMMARY"]
  end

  def test_unknown_source_warns_and_writes_empty_calendar
    assert_match(/unknown source "nope:x"/, warnings { build([feed(source: "nope:x")]) })
    assert_empty events
  end

  def test_missing_data_warns
    assert_match(/no data at "missing"/, warnings { build([feed(source: "data:missing")]) })
  end

  def test_feed_without_path_or_source_is_skipped
    data("events", [])
    site = nil
    assert_match(/skipping feed/, warnings { site = build([{ "path" => "feed.ics" }]) })
    refute site.pages.any? { |p| p.url == "/feed.ics" }
  end

  def test_where_filters_items
    data("events", [
      { "date" => "2026-11-05", "title" => "Public", "status" => "upcoming" },
      { "date" => "2026-11-06", "title" => "Old", "status" => "past" },
    ])
    build([feed(where: { "status" => "upcoming" })])

    assert_equal ["Public"], events.map { |e| e["SUMMARY"] }
  end

  # --- field mapping ---------------------------------------------------------

  def test_field_mapping_location_links_and_url
    data("events", [{
      "day" => "2026-11-05", "what" => "Talk", "where" => "Conf", "city" => "Köln",
      "abstract" => "About it", "slides" => "https://s.example/x", "page" => "/talks/x/",
    }])
    build([feed(fields: {
      "start" => "day", "title" => "what", "location" => %w[where city],
      "description" => "abstract", "url" => "page", "links" => { "Slides" => "slides" },
    })])

    event = events.first
    assert_equal "Talk", event["SUMMARY"]
    assert_equal "Conf\\, Köln", event["LOCATION"]
    assert_equal "About it\\n\\nSlides: https://s.example/x", event["DESCRIPTION"]
    assert_equal "https://example.org/talks/x/", event["URL"]
  end

  def test_optional_properties_are_omitted_when_empty
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    build([feed])

    event = events.first
    %w[LOCATION DESCRIPTION URL TRANSP].each { |key| refute event.key?(key), "#{key} should be omitted" }
  end

  def test_transparent
    data("events", [{ "date" => "2026-11-05", "title" => "A" }])
    build([feed(transparent: true)])

    assert_equal "TRANSPARENT", events.first["TRANSP"]
  end

  # --- uid -------------------------------------------------------------------

  def test_uid_is_stable_across_builds_and_independent_of_order
    a = { "date" => "2026-11-05", "title" => "A", "url" => "https://x/a" }
    b = { "date" => "2026-11-06", "title" => "B", "url" => "https://x/b" }

    data("events", [a, b])
    build([feed])
    first = events.to_h { |e| [e["SUMMARY"], e["UID"]] }

    data("events", [b, a])
    build([feed])
    second = events.to_h { |e| [e["SUMMARY"], e["UID"]] }

    assert_equal first, second
    refute_equal first["A"], first["B"]
    assert first["A"].end_with?("@example.org")
  end

  def test_uid_falls_back_to_date_and_title
    data("events", [{ "date" => "2026-11-05", "title" => "A" }, { "date" => "2026-11-05", "title" => "B" }])
    build([feed])

    uids = events.map { |e| e["UID"] }
    assert_equal 2, uids.uniq.size
  end

  # --- encoding --------------------------------------------------------------

  def test_escapes_text_values
    data("events", [{ "date" => "2026-11-05", "title" => "a, b; c\\d", "description" => "line 1\nline 2" }])
    build([feed])

    event = events.first
    assert_equal "a\\, b\\; c\\\\d", event["SUMMARY"]
    assert_equal "line 1\\nline 2", event["DESCRIPTION"]
  end

  def test_folds_long_lines_at_75_octets_without_splitting_utf8
    description = "Ä€😀 " * 60
    data("events", [{ "date" => "2026-11-05", "title" => "A", "description" => description }])
    build([feed])

    raw = read
    raw.split("\r\n").each do |line|
      assert_operator line.bytesize, :<=, 75, "line too long: #{line.inspect}"
      assert line.valid_encoding?, "folded line splits a UTF-8 character"
    end
    assert_equal description.strip, events.first["DESCRIPTION"]
  end

  # --- filter ----------------------------------------------------------------

  def test_webcal_filter
    write("index.html", "---\n---\n{{ 'https://example.org/feed.ics' | webcal }}|{{ 'http://x.org/a.ics' | webcal }}")
    build([])

    assert_equal "webcal://example.org/feed.ics|webcal://x.org/a.ics", File.read(File.join(@dest, "index.html"), encoding: "UTF-8")
  end
end
