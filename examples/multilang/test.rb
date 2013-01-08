require "json"
message = JSON.parse(STDIN.read)

message["count"].times do |i|
  puts i.to_json
end
