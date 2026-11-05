# frozen_string_literal: true

# Tests for _plugins/soft_delete.rb. Each test builds a throwaway Jekyll site
# in a temp dir and checks what templates and the iCal feed get to see.
#
# Run: bin/test

require "minitest/autorun"
require "jekyll"
require "tmpdir"
require "fileutils"
require "yaml"

class SoftDeleteTest < Minitest::Test
  PLUGINS_DIR = File.expand_path("../_plugins", __dir__)

  TALKS = [
    { "date" => "2026-12-09", "what" => "Visible", "where" => "Conf", "status" => "upcoming" },
    { "date" => "2026-12-09", "what" => "Cancelled", "where" => "Conf", "status" => "upcoming", "deleted" => true },
    { "date" => "2026-12-10", "what" => "Not deleted", "where" => "Conf", "status" => "upcoming", "deleted" => false },
  ].freeze

  def setup
    @source = Dir.mktmpdir("soft-delete-src")
    @dest = Dir.mktmpdir("soft-delete-site")
    write("_data/talks.yml", YAML.dump(TALKS))
    write("index.html", "---\n---\n{% for t in site.data.talks %}[{{ t.what }}]{% endfor %}")
  end

  def teardown
    FileUtils.rm_rf([@source, @dest])
  end

  def write(path, content)
    file = File.join(@source, path)
    FileUtils.mkdir_p(File.dirname(file))
    File.write(file, content)
  end

  def build(**config)
    site_config = {
      "source" => @source,
      "destination" => @dest,
      "plugins_dir" => PLUGINS_DIR,
      "url" => "https://example.org",
      "timezone" => "UTC",
      "quiet" => true,
    }.merge(config.transform_keys(&:to_s))
    Jekyll::Site.new(Jekyll.configuration(site_config)).tap(&:process)
  end

  def read(path)
    File.read(File.join(@dest, path), encoding: "UTF-8")
  end

  def test_deleted_talks_hidden_from_templates
    build
    html = read("index.html")
    assert_includes html, "[Visible]"
    assert_includes html, "[Not deleted]"
    refute_includes html, "Cancelled"
  end

  def test_deleted_talks_hidden_from_ical_feed
    build("ical_feeds" => [{ "path" => "talks.ics", "source" => "data:talks",
                             "fields" => { "title" => "what" } }])
    ics = read("talks.ics")
    assert_includes ics, "SUMMARY:Visible"
    refute_includes ics, "Cancelled"
  end

  def test_only_configured_data_files_filtered
    write("_data/other.yml", YAML.dump([{ "what" => "Kept", "deleted" => true }]))
    write("other.html", "---\n---\n{% for t in site.data.other %}[{{ t.what }}]{% endfor %}")
    build
    assert_includes read("other.html"), "[Kept]"
  end
end
