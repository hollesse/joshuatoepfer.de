# frozen_string_literal: true

# Soft delete for data files: entries with `deleted: true` are dropped from
# `site.data` before anything renders, so layouts, includes and generators
# (e.g. the iCal feed in ical_feed.rb) never see them. The entries stay in
# the YAML file, so a mistaken delete is undone by removing the flag.
#
# Applies to the data files listed under `soft_delete` in _config.yml
# (default: talks). The INNOQ talks sync (ADR-0007 §3a) sets
# `deleted: true` on talks INNOQ no longer lists, e.g. cancelled ones.
module JekyllSoftDelete
  class Generator < Jekyll::Generator
    safe true
    priority :highest

    def generate(site)
      Array(site.config.fetch("soft_delete", ["talks"])).each do |name|
        entries = site.data[name]
        next unless entries.is_a?(Array)

        site.data[name] = entries.reject { |e| e.is_a?(Hash) && e["deleted"] == true }
      end
    end
  end
end
