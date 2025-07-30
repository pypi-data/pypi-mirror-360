# This script will dump data data from the Talks CSV export into a list. It can
# beused for example to put all talks with all reviews in a pad instance, and
# have the content team discuss them items that need discussion.
#
# Output is sorted by score in ascending order, so you can set a  given score
# (say, 1.5) as a cutoff line, approve everything below that line, and discuss
# everything above it.
#
# Usage: ruby dump_talks_csv.rb /path/to/talks.csv

require 'csv'

# CSV Fields:
# talk_id
# title
# get_authors_display_name
# abstract
# talk_type.name
# track.name
# get_status_display
# review_score
# review_count
# notes
# private_notes
# all_review_comments

entries = []
csv = CSV.open(ARGV.first, headers: true)
csv.to_a.each do |row|
  unless row['get_status_display'] == 'Talk Withdrawn'
    entries << row
  end
end
entries.sort_by! do |e|
  e['review_score']
end

comment_start_idx = csv.headers.index('all_review_comments')

entries.each do |entry|
  puts 'Status: ' + entry['get_status_display']
  puts 'Title: ' + entry['title']
  puts 'Presenter(s): ' + entry['get_authors_display_name']
  puts 'Type: ' + String(entry['talk_type.name'])
  puts 'Track: ' + String(entry['track.name'])
  puts 'Score: ' + entry['review_score']
  puts 'Private notes: ' + String(entry['private_notes'])
  puts 'Reviewer Comments:'

  comments = []
  i = comment_start_idx
  while entry[i]
    comments << entry[i]
    i += 1
  end
  if comments.empty?
    comments = ['(none)']
  end
  comments.each do |c|
    c.lines.each do |l|
      puts '  ' + l
    end
  end
  puts
end
