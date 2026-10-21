# Generates /talks.ics — an iCalendar feed of all talks in _data/talks.yml,
# so the talk schedule can be subscribed to from any calendar app
# (webcal://joshuatoepfer.de/talks.ics).
#
# Talks only carry a date (no time), so every entry becomes an all-day event.
# Written as a generator rather than a Liquid template because RFC 5545
# requires text escaping and 75-octet line folding, which Liquid can't do
# cleanly.

require "date"
require "digest"

module TalksIcal
  class Generator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      talks = site.data["talks"] || []
      file = Jekyll::PageWithoutAFile.new(site, site.source, "", "talks.ics")
      file.content = Calendar.new(site, talks).to_s
      file.data["layout"] = nil
      file.data["sitemap"] = false
      site.pages << file
    end
  end

  class Calendar
    def initialize(site, talks)
      @site = site
      @talks = talks.sort_by { |t| t["date"].to_s }
      @stamp = site.time.utc.strftime("%Y%m%dT%H%M%SZ")
      @host = URI(site.config["url"].to_s).host || "joshuatoepfer.de"
    end

    def to_s
      lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//#{@host}//Talks//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:#{escape("Talks · #{@site.config.dig("author", "name")}")}",
        "X-WR-TIMEZONE:Europe/Berlin",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
      ]
      @talks.each { |t| lines.concat(event(t)) }
      lines << "END:VCALENDAR"
      lines.map { |l| fold(l) }.join("\r\n") + "\r\n"
    end

    private

    def event(t)
      date = Date.parse(t["date"].to_s)
      location = [t["where"], t["city"]].compact.join(", ")
      lines = [
        "BEGIN:VEVENT",
        "UID:#{uid(t)}",
        "DTSTAMP:#{@stamp}",
        "DTSTART;VALUE=DATE:#{date.strftime("%Y%m%d")}",
        "DTEND;VALUE=DATE:#{(date + 1).strftime("%Y%m%d")}",
        "SUMMARY:#{escape(t["what"])}",
        "LOCATION:#{escape(location)}",
        "DESCRIPTION:#{escape(description(t))}",
        "TRANSP:TRANSPARENT",
      ]
      lines << "URL:#{t["source_url"]}" if t["source_url"]
      lines << "END:VEVENT"
    end

    # Stable across builds so calendar apps update events instead of
    # duplicating them. INNOQ entries are keyed by source_url (as in the sync);
    # manual entries by date + title.
    def uid(t)
      key = t["source_url"] || "#{t["date"]}|#{t["what"]}"
      "#{Digest::SHA1.hexdigest(key.to_s)}@#{@host}"
    end

    def description(t)
      parts = []
      parts << t["abstract"].to_s.strip if t["abstract"]
      parts << "Slides: #{t["slides"]}" if t["slides"]
      parts << "Video: #{t["video"]}" if t["video"]
      parts << "Mehr: #{t["source_url"]}" if t["source_url"]
      parts.join("\n\n")
    end

    def escape(text)
      text.to_s
        .gsub("\\", "\\\\\\\\")
        .gsub(";", "\\;")
        .gsub(",", "\\,")
        .gsub(/\r?\n/, "\\n")
    end

    # RFC 5545 §3.1: lines longer than 75 octets are folded with CRLF + space,
    # without splitting multi-byte UTF-8 characters.
    def fold(line)
      out = []
      current = +""
      limit = 75
      line.each_char do |ch|
        if current.bytesize + ch.bytesize > limit
          out << current
          current = +""
          limit = 74 # continuation lines start with a space
        end
        current << ch
      end
      out << current
      out.join("\r\n ")
    end
  end
end
