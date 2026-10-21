# frozen_string_literal: true

# jekyll-ical-feed — generates subscribable iCalendar (.ics) feeds from data
# files or collections. Self-contained so it can be lifted into a gem as-is.
#
# Configure one or more feeds in _config.yml:
#
#   ical_feeds:
#     - path: talks.ics                 # output path (required)
#       source: data:talks              # data:<file>[.<key>…] | collection:<label> | posts (required)
#       name: "Talks"                   # calendar name shown in clients (default: site.title)
#       timezone: Europe/Berlin         # X-WR-TIMEZONE hint (default: site.timezone)
#       refresh: PT12H                  # refresh hint for clients, ISO 8601 duration
#       where: { status: upcoming }     # optional: only items whose fields equal these values
#       transparent: true               # optional: events don't block time (show as "free")
#       all_day: auto                   # auto: dates and midnight times are all-day; or true/false
#       fields:                         # where each event property comes from; defaults shown
#         start: date                   # Date → all-day event, Time/datetime → timed event
#         end: end                      # optional; else start + duration (timed) or + 1 day
#         duration: duration            # minutes, only used for timed events
#         title: title
#         location: location            # a field name, or a list joined with ", "
#         description: description
#         url: url                      # absolute or site-relative URL
#         uid: url                      # stable key so clients update instead of duplicating
#         links: {}                     # { "Slides": slides } → appended to the description
#
# A field mapping can also be a Liquid template over the item's fields, e.g.
#   title: "{{ where }}: {{ what }}"
# An empty result counts as a missing value.
#
# In collections the fields are front matter (plus `url`, `content`).
# Use the `webcal` filter to link a feed for one-click subscription:
#   {{ '/talks.ics' | absolute_url | webcal }}

require "date"
require "digest"
require "time"
require "uri"

module JekyllIcalFeed
  DEFAULT_FIELDS = {
    "start" => "date",
    "end" => "end",
    "duration" => "duration",
    "title" => "title",
    "location" => "location",
    "description" => "description",
    "url" => "url",
    "uid" => "url",
    "links" => {},
  }.freeze

  class Generator < Jekyll::Generator
    safe true
    priority :lowest

    def generate(site)
      Array(site.config["ical_feeds"]).each do |config|
        unless config["path"] && config["source"]
          Jekyll.logger.warn "ical_feed:", "skipping feed without `path` and `source`: #{config.inspect}"
          next
        end
        page = Jekyll::PageWithoutAFile.new(site, site.source, File.dirname(config["path"]), File.basename(config["path"]))
        page.content = Feed.new(site, config).to_s
        page.data["layout"] = nil
        page.data["sitemap"] = false
        site.pages << page
      end
    end
  end

  class Feed
    def initialize(site, config)
      @site = site
      @config = config
      @fields = DEFAULT_FIELDS.merge(config["fields"] || {})
      @stamp = site.time.utc.strftime("%Y%m%dT%H%M%SZ")
      @host = URI(site.config["url"].to_s).host || "localhost"
    end

    def to_s
      lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//#{@host}//jekyll-ical-feed//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:#{escape(@config["name"] || @site.config["title"])}",
      ]
      timezone = @config["timezone"] || @site.config["timezone"]
      lines << "X-WR-TIMEZONE:#{timezone}" if timezone
      if (refresh = @config["refresh"])
        lines << "REFRESH-INTERVAL;VALUE=DURATION:#{refresh}"
        lines << "X-PUBLISHED-TTL:#{refresh}"
      end
      items.each { |item| lines.concat(event(item)) }
      lines << "END:VCALENDAR"
      lines.map { |l| fold(l) }.join("\r\n") + "\r\n"
    end

    private

    def items
      list = source_items.select { |i| self.class.matches?(i, @config["where"]) && value(i, "start") }
      list.sort_by { |i| value(i, "start").to_s }
    end

    def source_items
      kind, name = @config["source"].to_s.split(":", 2)
      case kind
      when "data"
        data = name.to_s.split(".").reduce(@site.data) { |d, k| d.is_a?(Hash) ? d[k] : nil }
        data ? Array(data) : warn_empty("no data at #{name.inspect}")
      when "collection", "posts"
        collection = @site.collections[name || "posts"]
        return warn_empty("unknown collection #{name.inspect}") unless collection

        collection.docs.map { |doc| doc.data.merge("url" => doc.url, "content" => doc.content) }
      else
        warn_empty("unknown source #{@config["source"].inspect}")
      end
    end

    def warn_empty(message)
      Jekyll.logger.warn "ical_feed:", "#{@config["path"]}: #{message}"
      []
    end

    def self.matches?(item, where)
      return true unless where

      where.all? { |k, v| item[k].to_s == v.to_s }
    end

    def event(item)
      start = to_time_or_date(value(item, "start"))
      finish = to_time_or_date(value(item, "end")) || default_end(item, start)
      lines = ["BEGIN:VEVENT", "UID:#{uid(item)}", "DTSTAMP:#{@stamp}", *dtline("DTSTART", start), *dtline("DTEND", finish)]
      lines << "SUMMARY:#{escape(value(item, "title"))}"
      location = Array(@fields["location"]).filter_map { |f| item[f] }.join(", ")
      lines << "LOCATION:#{escape(location)}" unless location.empty?
      description = description(item)
      lines << "DESCRIPTION:#{escape(description)}" unless description.empty?
      url = absolute(value(item, "url"))
      lines << "URL:#{url}" if url
      lines << "TRANSP:TRANSPARENT" if @config["transparent"]
      lines << "END:VEVENT"
    end

    def value(item, field)
      key = @fields[field]
      return nil unless key.is_a?(String)
      return item[key] unless key.include?("{{") || key.include?("{%")

      rendered = template(key).render!(item, registers: { site: @site }, filters: [Jekyll::Filters]).strip
      rendered.empty? ? nil : rendered
    end

    def template(source)
      (@templates ||= {})[source] ||= Liquid::Template.parse(source)
    end

    def to_time_or_date(raw)
      case raw
      when nil, "" then nil
      when /\A\d{4}-\d{2}-\d{2}\z/ then all_day(Date.parse(raw))
      else all_day(raw.is_a?(Date) || raw.is_a?(Time) ? raw : Time.parse(raw.to_s))
      end
    end

    # Front matter `date: 2026-12-01` arrives as a midnight Time, so in auto
    # mode a midnight Time counts as a plain date.
    def all_day(t)
      mode = @config.fetch("all_day", "auto").to_s
      midnight = t.is_a?(Time) && [t.hour, t.min, t.sec] == [0, 0, 0]
      return t.to_date if mode == "true" || (mode == "auto" && midnight)
      return Time.new(t.year, t.month, t.day) if mode == "false" && !t.is_a?(Time)

      t
    end

    def default_end(item, start)
      return start + 1 if start.is_a?(Date)

      start + (value(item, "duration") || 60).to_i * 60
    end

    def dtline(name, t)
      t.is_a?(Time) ? "#{name}:#{t.utc.strftime("%Y%m%dT%H%M%SZ")}" : "#{name};VALUE=DATE:#{t.strftime("%Y%m%d")}"
    end

    def uid(item)
      key = value(item, "uid") || "#{value(item, "start")}|#{value(item, "title")}"
      "#{Digest::SHA1.hexdigest(key.to_s)}@#{@host}"
    end

    def description(item)
      parts = [value(item, "description").to_s.strip]
      (@fields["links"] || {}).each { |label, key| parts << "#{label}: #{absolute(item[key])}" if item[key] }
      parts.reject(&:empty?).join("\n\n")
    end

    def absolute(url)
      return nil if url.nil? || url.to_s.empty?
      return url.to_s if url.to_s.match?(%r{\A[a-z]+://}i)

      "#{@site.config["url"]}#{@site.config["baseurl"]}#{url}"
    end

    def escape(text)
      text.to_s.gsub("\\") { "\\\\" }.gsub(";", "\\;").gsub(",", "\\,").gsub(/\r?\n/, "\\n")
    end

    # RFC 5545 §3.1: fold lines at 75 octets without splitting UTF-8 characters.
    def fold(line)
      out = [+""]
      line.each_char do |ch|
        limit = out.size == 1 ? 75 : 74 # continuation lines start with a space
        out << +"" if out.last.bytesize + ch.bytesize > limit
        out.last << ch
      end
      out.join("\r\n ")
    end
  end

  module Filters
    # Turns an http(s) URL into webcal:// so calendar apps offer to subscribe.
    def webcal(url)
      url.to_s.sub(%r{\Ahttps?://}i, "webcal://")
    end
  end
end

Liquid::Template.register_filter(JekyllIcalFeed::Filters)
